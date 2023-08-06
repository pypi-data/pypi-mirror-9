/**
 * @date Tue Jul 19 15:33:20 2011 +0200
 * @author Francois Moulin <Francois.Moulin@idiap.ch>
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.learn.em/ZTNorm.h>
#include <bob.core/assert.h>
#include <limits>


static void _ztNorm(const blitz::Array<double,2>& rawscores_probes_vs_models,
            const blitz::Array<double,2>* rawscores_zprobes_vs_models,
            const blitz::Array<double,2>* rawscores_probes_vs_tmodels,
            const blitz::Array<double,2>* rawscores_zprobes_vs_tmodels,
            const blitz::Array<bool,2>* mask_zprobes_vs_tmodels_istruetrial,
            blitz::Array<double,2>& scores)
{
  // Rename variables
  const blitz::Array<double,2>& A = rawscores_probes_vs_models;
  const blitz::Array<double,2>* B = rawscores_zprobes_vs_models;
  const blitz::Array<double,2>* C = rawscores_probes_vs_tmodels;
  const blitz::Array<double,2>* D = rawscores_zprobes_vs_tmodels;

  // Compute the sizes
  int size_eval  = A.extent(0);
  int size_enroll = A.extent(1);
  int size_tnorm = (C ? C->extent(0) : 0);
  int size_znorm = (B ? B->extent(1) : 0);

  // Check the inputs
  bob::core::array::assertSameDimensionLength(A.extent(0), size_eval);
  bob::core::array::assertSameDimensionLength(A.extent(1), size_enroll);

  if (B) {
    bob::core::array::assertSameDimensionLength(B->extent(1), size_znorm);
    if (size_znorm > 0)
      bob::core::array::assertSameDimensionLength(B->extent(0), size_eval);
  }

  if (C) {
    bob::core::array::assertSameDimensionLength(C->extent(0), size_tnorm);
    if (size_tnorm > 0)
      bob::core::array::assertSameDimensionLength(C->extent(1), size_enroll);
  }

  if (D && size_znorm > 0 && size_tnorm > 0) {
    bob::core::array::assertSameDimensionLength(D->extent(0), size_tnorm);
    bob::core::array::assertSameDimensionLength(D->extent(1), size_znorm);
  }

  if (mask_zprobes_vs_tmodels_istruetrial) {
    bob::core::array::assertSameDimensionLength(mask_zprobes_vs_tmodels_istruetrial->extent(0), size_tnorm);
    bob::core::array::assertSameDimensionLength(mask_zprobes_vs_tmodels_istruetrial->extent(1), size_znorm);
  }

  bob::core::array::assertSameDimensionLength(scores.extent(0), size_eval);
  bob::core::array::assertSameDimensionLength(scores.extent(1), size_enroll);

  // Declare needed IndexPlaceholder
  blitz::firstIndex ii;
  blitz::secondIndex jj;

  // Constant to check if the std is close to 0.
  const double eps = std::numeric_limits<double>::min();

  // zA
  blitz::Array<double,2> zA(A.shape());
  if (B && size_znorm > 0) {
    // Znorm  -->      zA  = (A - mean(B) ) / std(B)    [znorm on oringinal scores]
    // mean(B)
    blitz::Array<double,1> mean_B(blitz::mean(*B, jj));
    // std(B)
    blitz::Array<double,2> B2n(B->shape());
    B2n = blitz::pow2((*B)(ii, jj) - mean_B(ii));
    blitz::Array<double,1> std_B(B->extent(0));
    if(size_znorm>1)
      std_B = blitz::sqrt(blitz::sum(B2n, jj) / (size_znorm - 1));
    else // 1 single value -> std = 0
      std_B = 0;
    std_B = blitz::where( std_B <= eps, 1., std_B);

    zA = (A(ii, jj) - mean_B(ii)) / std_B(ii);
  }
  else
    zA = A;

  blitz::Array<double,2> zC(size_tnorm, size_enroll);
  if (D && size_tnorm > 0 && size_znorm > 0) {
    blitz::Array<double,1> mean_Dimp(size_tnorm);
    blitz::Array<double,1> std_Dimp(size_tnorm);

    // Compute mean_Dimp and std_Dimp = D only with impostors
    for (int i = 0; i < size_tnorm; ++i) {
      double sum = 0;
      double sumsq = 0;
      double count = 0;
      for (int j = 0; j < size_znorm; ++j) {
        bool keep;
        // The second part is never executed if mask_zprobes_vs_tmodels_istruetrial==NULL
        keep = (mask_zprobes_vs_tmodels_istruetrial == NULL) || !(*mask_zprobes_vs_tmodels_istruetrial)(i, j); //tnorm_models_spk_ids(i) != znorm_tests_spk_ids(j);

        double value = keep * (*D)(i, j);
        sum += value;
        sumsq += value*value;
        count += keep;
      }

      double mean = sum / count;
      mean_Dimp(i) = mean;
      if (count > 1)
        std_Dimp(i) = sqrt((sumsq - count * mean * mean) / (count -1));
      else // 1 single value -> std = 0
        std_Dimp(i) = 0;
    }

    // zC  = (C - mean(D)) / std(D)     [znorm the tnorm scores]
    std_Dimp = blitz::where( std_Dimp <= eps, 1., std_Dimp);
    zC = ((*C)(ii, jj) - mean_Dimp(ii)) / std_Dimp(ii);
  }
  else if (C && size_tnorm > 0)
    zC = *C;

  if (C && size_tnorm > 0)
  {
    blitz::Array<double,1> mean_zC(size_enroll);
    blitz::Array<double,1> std_zC(size_enroll);

    // ztA = (zA - mean(zC)) / std(zC)  [ztnorm on eval scores]
    mean_zC = blitz::mean(zC(jj, ii), jj);
    if (size_tnorm > 1)
      std_zC = sqrt(blitz::sum(pow(zC(jj, ii) - mean_zC(ii), 2) , jj) / (size_tnorm - 1));
    else // 1 single value -> std = 0
      std_zC = 0;
    std_zC = blitz::where( std_zC <= eps, 1., std_zC);

    // Normalised scores
    scores = (zA(ii, jj) - mean_zC(jj)) /  std_zC(jj);
  }
  else
    scores = zA;
}

void bob::learn::em::ztNorm(const blitz::Array<double,2>& rawscores_probes_vs_models,
            const blitz::Array<double,2>& rawscores_zprobes_vs_models,
            const blitz::Array<double,2>& rawscores_probes_vs_tmodels,
            const blitz::Array<double,2>& rawscores_zprobes_vs_tmodels,
            const blitz::Array<bool,2>& mask_zprobes_vs_tmodels_istruetrial,
            blitz::Array<double,2>& scores)
{
  _ztNorm(rawscores_probes_vs_models, &rawscores_zprobes_vs_models, &rawscores_probes_vs_tmodels,
                 &rawscores_zprobes_vs_tmodels, &mask_zprobes_vs_tmodels_istruetrial, scores);
}

void bob::learn::em::ztNorm(const blitz::Array<double,2>& rawscores_probes_vs_models,
            const blitz::Array<double,2>& rawscores_zprobes_vs_models,
            const blitz::Array<double,2>& rawscores_probes_vs_tmodels,
            const blitz::Array<double,2>& rawscores_zprobes_vs_tmodels,
            blitz::Array<double,2>& scores)
{
  _ztNorm(rawscores_probes_vs_models, &rawscores_zprobes_vs_models, &rawscores_probes_vs_tmodels,
                 &rawscores_zprobes_vs_tmodels, NULL, scores);
}

void bob::learn::em::tNorm(const blitz::Array<double,2>& rawscores_probes_vs_models,
           const blitz::Array<double,2>& rawscores_probes_vs_tmodels,
           blitz::Array<double,2>& scores)
{
  _ztNorm(rawscores_probes_vs_models, NULL, &rawscores_probes_vs_tmodels,
                 NULL, NULL, scores);
}

void bob::learn::em::zNorm(const blitz::Array<double,2>& rawscores_probes_vs_models,
           const blitz::Array<double,2>& rawscores_zprobes_vs_models,
           blitz::Array<double,2>& scores)
{
  _ztNorm(rawscores_probes_vs_models, &rawscores_zprobes_vs_models, NULL,
                 NULL, NULL, scores);
}
