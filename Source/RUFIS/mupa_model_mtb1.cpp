// #define QI_DEBUG_BUILD 1
#include "Macro.h"
#include "mupa_model_mtb1.h"
#include "rufis_ss.hpp"

using AugMat = Eigen::Matrix<double, 5, 5>; // Short for Augmented Matrix
using AugVec = Eigen::Vector<double, 5>;

auto MUPAMTB1Model::signal(VaryingArray const &v, FixedArray const &f) const -> QI_ARRAY(double) {
    using T = double;

    T const &M0_f = v[0];
    T const &R1_f = 1. / v[1];
    T const &R1_b = R1_f;
    T const &R2_f = 1. / v[2];
    T const &M0_b = v[3];
    T const &k    = 4.3;
    T const &k_bf = k * M0_f;
    T const &k_fb = k * M0_b;
    T const &B1   = f[0];

    AugMat R;
    R << -R2_f, 0, 0, 0, 0,          //
        0, -R2_f, 0, 0, 0,           //
        0, 0, -R1_f, 0, M0_f * R1_f, //
        0, 0, 0, -R1_b, M0_b * R1_b, //
        0, 0, 0, 0, 0;

    AugMat K;
    K << 0, 0, 0, 0, 0,       //
        0, 0, 0, 0, 0,        //
        0, 0, -k_fb, k_bf, 0, //
        0, 0, k_fb, -k_bf, 0, //
        0, 0, 0, 0, 0;

    AugMat const S = Eigen::DiagonalMatrix<double, 5, 5>({0, 0, 1., 1., 1.}).toDenseMatrix();

    AugMat const RpK = R + K;

    // Setup readout segment matrices
    AugMat const        ramp = (RpK * sequence.Tramp).exp();
    std::vector<AugMat> TR_mats(sequence.FA.rows());
    std::vector<AugMat> seg_mats(sequence.FA.rows());
    for (int is = 0; is < sequence.FA.rows(); is++) {
        double const B1x = B1 * sequence.FA[is] / sequence.Trf[is];
        double const W   = M_PI * lineshape(0, lineshape.T2_nominal) * B1x * B1x;
        AugMat       rf;
        rf << 0, 0, 0, 0, 0,  //
            0, 0, B1x, 0, 0,  //
            0, -B1x, 0, 0, 0, //
            0, 0, 0, -W, 0,   //
            0, 0, 0, 0, 0;
        AugMat const Rrd = (RpK * (sequence.TR - sequence.Trf[is])).exp();
        AugMat const Ard = ((RpK + rf) * sequence.Trf[is]).exp();
        TR_mats[is]      = S * Rrd * Ard;
        seg_mats[is]     = TR_mats[is].pow(sequence.SPS);
    }

    // Setup pulse matrices
    std::vector<AugMat> prep_mats(sequence.size());
    for (int is = 0; is < sequence.size(); is++) {
        auto const & name = sequence.prep[is];
        auto const & p    = sequence.prep_pulses[name];
        double const W    = M_PI * 1.4e-5 * B1 * B1 * p.int_b1_sq;
        AugMat       C;
        C << 0, 0, 0, 0, 0,                                    //
            0, 0, 0, 0, 0,                                     //
            0, 0, exp(-R2_f * p.T_trans) * cos(p.FAeff), 0, 0, //
            0, 0, 0, exp(-W), 0,                               //
            0, 0, 0, 0, 1;
        prep_mats[is] = C;
    }

    // First calculate the system matrix
    AugMat X = AugMat::Identity();
    for (int is = 0; is < sequence.size(); is++) {
        X = ramp * seg_mats[is] * ramp * S * prep_mats[is] * X;
    }
    AugVec m_ss = SolveSteadyState(X);

    // Now loop through the segments and record the signal for each
    Eigen::ArrayXd sig(sequence.size());
    QI_DBVEC(m_ss);
    AugVec m_aug = m_ss;
    for (int is = 0; is < sequence.size(); is++) {
        m_aug             = ramp * S * prep_mats[is] * m_aug;
        auto       m_gm   = GeometricAvg(TR_mats[is], seg_mats[is], m_aug, sequence.SPS);
        auto const signal = m_gm[2] * sin(B1 * sequence.FA[is]);
        sig[is]           = signal;
        m_aug             = ramp * seg_mats[is] * m_aug;
        QI_DBVEC(m_gm);
    }
    QI_DBVEC(v);
    QI_DBVEC(sig);
    return sig;
}

void MUPAMTB1Model::derived(const VaryingArray &varying,
                            const FixedArray & /* Unused */,
                            DerivedArray &derived) const {
    const auto &M0_f = varying[0];
    const auto &M0_b = varying[3];
    derived[0]       = 100.0 * M0_b / (M0_f + M0_b);
}