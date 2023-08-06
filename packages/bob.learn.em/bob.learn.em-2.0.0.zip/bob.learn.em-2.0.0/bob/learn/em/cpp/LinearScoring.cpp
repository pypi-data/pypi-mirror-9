/**
 * @date Wed Jul 13 16:00:04 2011 +0200
 * @author Francois Moulin <Francois.Moulin@idiap.ch>
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */
#include <bob.learn.em/LinearScoring.h>
#include <bob.math/linear.h>


static void _linearScoring(const std::vector<blitz::Array<double,1> >& models,
                   const blitz::Array<double,1>& ubm_mean,
                   const blitz::Array<double,1>& ubm_variance,
                   const std::vector<boost::shared_ptr<const bob::learn::em::GMMStats> >& test_stats,
                   const std::vector<blitz::Array<double,1> >* test_channelOffset,
                   const bool frame_length_normalisation,
                   blitz::Array<double,2>& scores)
{
  int C = test_stats[0]->sumPx.extent(0);
  int D = test_stats[0]->sumPx.extent(1);
  int CD = C*D;
  int Tt = test_stats.size();
  int Tm = models.size();

  // Check output size
  bob::core::array::assertSameDimensionLength(scores.extent(0), models.size());
  bob::core::array::assertSameDimensionLength(scores.extent(1), test_stats.size());

  blitz::Array<double,2> A(Tm, CD);
  blitz::Array<double,2> B(CD, Tt);

  // 1) Compute A
  for(int t=0; t<Tm; ++t) {
    blitz::Array<double, 1> tmp = A(t, blitz::Range::all());
    tmp = (models[t] - ubm_mean) / ubm_variance;
  }

  // 2) Compute B
  if(test_channelOffset == 0) {
    for(int t=0; t<Tt; ++t)
      for(int s=0; s<CD; ++s)
        B(s, t) = test_stats[t]->sumPx(s/D, s%D) - (ubm_mean(s) * test_stats[t]->n(s/D));
  }
  else {
    bob::core::array::assertSameDimensionLength((*test_channelOffset).size(), Tt);

    for(int t=0; t<Tt; ++t) {
      bob::core::array::assertSameDimensionLength((*test_channelOffset)[t].extent(0), CD);
      for(int s=0; s<CD; ++s)
        B(s, t) = test_stats[t]->sumPx(s/D, s%D) - (test_stats[t]->n(s/D) * (ubm_mean(s) + (*test_channelOffset)[t](s)));
    }
  }

  // Apply the normalisation if needed
  if(frame_length_normalisation) {
    for(int t=0; t<Tt; ++t) {
      double sum_N = test_stats[t]->T;
      blitz::Array<double, 1> v_t = B(blitz::Range::all(),t);

      if (sum_N <= std::numeric_limits<double>::epsilon() && sum_N >= -std::numeric_limits<double>::epsilon())
        v_t = 0;
      else
        v_t /= sum_N;
    }
  }

  // 3) Compute LLR
  bob::math::prod(A, B, scores);
}


void bob::learn::em::linearScoring(const std::vector<blitz::Array<double,1> >& models,
                   const blitz::Array<double,1>& ubm_mean, const blitz::Array<double,1>& ubm_variance,
                   const std::vector<boost::shared_ptr<const bob::learn::em::GMMStats> >& test_stats,
                   const std::vector<blitz::Array<double,1> >& test_channelOffset,
                   const bool frame_length_normalisation,
                   blitz::Array<double, 2>& scores)
{
  _linearScoring(models, ubm_mean, ubm_variance, test_stats, &test_channelOffset, frame_length_normalisation, scores);
}

void bob::learn::em::linearScoring(const std::vector<blitz::Array<double,1> >& models,
                   const blitz::Array<double,1>& ubm_mean, const blitz::Array<double,1>& ubm_variance,
                   const std::vector<boost::shared_ptr<const bob::learn::em::GMMStats> >& test_stats,
                   const bool frame_length_normalisation,
                   blitz::Array<double, 2>& scores)
{
  _linearScoring(models, ubm_mean, ubm_variance, test_stats, 0, frame_length_normalisation, scores);
}

void bob::learn::em::linearScoring(const std::vector<boost::shared_ptr<const bob::learn::em::GMMMachine> >& models,
                   const bob::learn::em::GMMMachine& ubm,
                   const std::vector<boost::shared_ptr<const bob::learn::em::GMMStats> >& test_stats,
                   const bool frame_length_normalisation,
                   blitz::Array<double, 2>& scores)
{
  int C = test_stats[0]->sumPx.extent(0);
  int D = test_stats[0]->sumPx.extent(1);
  int CD = C*D;
  std::vector<blitz::Array<double,1> > models_b;
  // Allocate and get the mean supervector
  for(size_t i=0; i<models.size(); ++i) {
    blitz::Array<double,1> mod(CD);
    mod = models[i]->getMeanSupervector();
    models_b.push_back(mod);
  }
  const blitz::Array<double,1>& ubm_mean = ubm.getMeanSupervector();
  const blitz::Array<double,1>& ubm_variance = ubm.getVarianceSupervector();
  _linearScoring(models_b, ubm_mean, ubm_variance, test_stats, 0, frame_length_normalisation, scores);
}

void bob::learn::em::linearScoring(const std::vector<boost::shared_ptr<const bob::learn::em::GMMMachine> >& models,
                   const bob::learn::em::GMMMachine& ubm,
                   const std::vector<boost::shared_ptr<const bob::learn::em::GMMStats> >& test_stats,
                   const std::vector<blitz::Array<double,1> >& test_channelOffset,
                   const bool frame_length_normalisation,
                   blitz::Array<double, 2>& scores)
{
  int C = test_stats[0]->sumPx.extent(0);
  int D = test_stats[0]->sumPx.extent(1);
  int CD = C*D;
  std::vector<blitz::Array<double,1> > models_b;
  // Allocate and get the mean supervector
  for(size_t i=0; i<models.size(); ++i) {
    blitz::Array<double,1> mod(CD);
    mod = models[i]->getMeanSupervector();
    models_b.push_back(mod);
  }
  const blitz::Array<double,1>& ubm_mean = ubm.getMeanSupervector();
  const blitz::Array<double,1>& ubm_variance = ubm.getVarianceSupervector();
  _linearScoring(models_b, ubm_mean, ubm_variance, test_stats, &test_channelOffset, frame_length_normalisation, scores);
}



double bob::learn::em::linearScoring(const blitz::Array<double,1>& models,
                     const blitz::Array<double,1>& ubm_mean, const blitz::Array<double,1>& ubm_variance,
                     const bob::learn::em::GMMStats& test_stats,
                     const blitz::Array<double,1>& test_channelOffset,
                     const bool frame_length_normalisation)
{
  int C = test_stats.sumPx.extent(0);
  int D = test_stats.sumPx.extent(1);
  int CD = C*D;


  blitz::Array<double,1> A(CD);
  blitz::Array<double,1> B(CD);

  // 1) Compute A
  A = (models - ubm_mean) / ubm_variance;

  // 2) Compute B
  for (int s=0; s<CD; ++s)
    B(s) = test_stats.sumPx(s/D, s%D) - (test_stats.n(s/D) * (ubm_mean(s) + test_channelOffset(s)));

  // Apply the normalisation if needed
  if (frame_length_normalisation) {
    double sum_N = test_stats.T;
    if (sum_N == 0)
      B = 0;
    else
      B /= sum_N;
  }

  return blitz::sum(A * B);
}

