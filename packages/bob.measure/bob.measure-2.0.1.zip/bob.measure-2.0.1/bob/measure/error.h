/**
 * @date Wed Apr 20 08:02:30 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief A set of methods that evaluates error from score sets
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_MEASURE_ERROR_H
#define BOB_MEASURE_ERROR_H

#include <blitz/array.h>
#include <utility>
#include <vector>

namespace bob { namespace measure {

  /**
   * Calculates the FA ratio and the FR ratio given positive and negative
   * scores and a threshold. 'positives' holds the score information for
   * samples that are labeled to belong to a certain class (a.k.a., "signal"
   * or "client"). 'negatives' holds the score information for samples that are
   * labeled *not* to belong to the class (a.k.a., "noise" or "impostor").
   *
   * It is expected that 'positive' scores are, at least by design, greater
   * than 'negative' scores. So, every positive value that falls bellow the
   * threshold is considered a false-rejection (FR). 'negative' samples that
   * fall above the threshold are considered a false-accept (FA).
   *
   * Positives that fall on the threshold (exactly) are considered correctly
   * classified. Negatives that fall on the threshold (exactly) are considered
   * *incorrectly* classified. This equivalent to setting the comparison like
   * this pseudo-code:
   *
   * foreach (positive as K) if K < threshold: falseRejectionCount += 1
   * foreach (negative as K) if K >= threshold: falseAcceptCount += 1
   *
   * The 'threshold' value does not necessarily have to fall in the range
   * covered by the input scores (negatives and positives altogether), but if
   * it does not, the output will be either (1.0, 0.0) or (0.0, 1.0)
   * depending on the side the threshold falls.
   *
   * The output is in form of a std::pair of two double-precision real numbers.
   * The numbers range from 0 to 1. The first element of the pair is the
   * false-accept ratio. The second element of the pair is the false-rejection
   * ratio.
   *
   * It is possible that scores are inverted in the negative/positive sense. In
   * some setups the designer may have setup the system so 'positive' samples
   * have a smaller score than the 'negative' ones. In this case, make sure you
   * normalize the scores so positive samples have greater scores before
   * feeding them into this method.
   */
  std::pair<double, double> farfrr(const blitz::Array<double,1>& negatives,
      const blitz::Array<double,1>& positives, double threshold);

  /**
   * Calculates the precision and recall (sensitiveness) values given positive and negative
   * scores and a threshold. 'positives' holds the score information for
   * samples that are labeled to belong to a certain class (a.k.a., "signal"
   * or "client"). 'negatives' holds the score information for samples that are
   * labeled *not* to belong to the class (a.k.a., "noise" or "impostor").
   *
   * For more precise details about how the method considers error rates, please refer to the documentation of the method bob.measure.farfrr. 
   *
   * It is possible that scores are inverted in the negative/positive sense. In
   * some setups the designer may have setup the system so 'positive' samples
   * have a smaller score than the 'negative' ones. In this case, make sure you
   * normalize the scores so positive samples have greater scores before
   * feeding them into this method.
   */
  std::pair<double, double> precision_recall(const blitz::Array<double,1>& negatives,
      const blitz::Array<double,1>& positives, double threshold);

  /**
   * This method computes F score of the accuracy of the classification. It is a weighted mean of precision and recall measurements. The weight parameter needs to be non-negative real value. In case the weight parameter is 1, the F-score is called F1 score and is a harmonic mean between precision and recall values.
   */
  double f_score(const blitz::Array<double,1>& negatives,
    const blitz::Array<double,1>& positives, double threshold, double weight) ;

  /**
   * This method returns a blitz::Array composed of booleans that pin-point
   * which positives where correctly classified in a 'positive' score sample,
   * given a threshold. It runs the formula:
   *
   * foreach (element k in positive)
   *   if positive[k] >= threshold: returnValue[k] = true
   *   else: returnValue[k] = false
   */
  inline blitz::Array<bool,1> correctlyClassifiedPositives
    (const blitz::Array<double,1>& positives, double threshold) {
      return blitz::Array<bool,1>(positives >= threshold);
    }

  /**
   * This method returns a blitz::Array composed of booleans that pin-point
   * which negatives where correctly classified in a 'negative' score sample,
   * given a threshold. It runs the formula:
   *
   * foreach (element k in negative)
   *   if negative[k] < threshold: returnValue[k] = true
   *   else: returnValue[k] = false
   */
  inline blitz::Array<bool,1> correctlyClassifiedNegatives
    (const blitz::Array<double,1>& negatives, double threshold) {
      return blitz::Array<bool,1>(negatives < threshold);
    }

  /**
   * Recursively minimizes w.r.t. to the given predicate method. Please refer
   * to minimizingThreshold() for a full explanation. This method is only
   * supposed to be used through that method.
   */
  template <typename T>
  static double recursive_minimization(const blitz::Array<double,1>& negatives,
      const blitz::Array<double,1>& positives, T& predicate,
      double min, double max, size_t steps) {
    static const double QUIT_THRESHOLD = 1e-10;
    const double diff = max - min;
    const double too_small = std::abs(diff/max);

    //if the difference between max and min is too small, we quit.
    if ( too_small < QUIT_THRESHOLD ) return min; //or max, does not matter...

    double step_size = diff/(double)steps;
    double min_value = predicate(1.0, 0.0); ///< to the left of the range

    //the accumulator holds the thresholds that given the minimum value for the
    //input predicate.
    std::vector<double> accumulator;
    accumulator.reserve(steps);

    for (size_t i=0; i<steps; ++i) {
      double threshold = ((double)i * step_size) + min;

      std::pair<double, double> ratios =
        farfrr(negatives, positives, threshold);

      double current_cost = predicate(ratios.first, ratios.second);

      if (current_cost < min_value) {
        min_value = current_cost;
        accumulator.clear(); ///< clean-up, we got a better minimum
        accumulator.push_back(threshold); ///< remember this threshold
      }
      else if (std::abs(current_cost - min_value) < 1e-16) {
        //accumulate to later decide...
        accumulator.push_back(threshold);
      }
    }

    //we stop when it doesn't matter anymore to threshold.
    if (accumulator.size() != steps) {
      //still needs some refinement: pick-up the middle of the range and go
      return recursive_minimization(negatives, positives, predicate,
          accumulator[accumulator.size()/2]-step_size,
          accumulator[accumulator.size()/2]+step_size,
          steps);
    }

    return accumulator[accumulator.size()/2];
  }

  /**
   * This method can calculate a threshold based on a set of scores (positives
   * and negatives) given a certain minimization criteria, input as a
   * functional predicate. For a discussion on 'positive' and 'negative' see
   * bob::measure::farfrr().
   *
   * The predicate method gives back the current minimum given false-acceptance
   * (FA) and false-rejection (FR) ratios for the input data. As a predicate,
   * it has to be a non-member method or a pre-configured functor where we can
   * use operator(). The API for the method is:
   *
   * double predicate(double fa_ratio, double fr_ratio);
   *
   * Please note that this method will only work with single-minimum smooth
   * predicates.
   *
   * The minimization is carried out in a recursive manner. First, we identify
   * the threshold that minimizes the predicate given a set of N (N=100)
   * thresholds between the min(negatives, positives) and the max(negatives,
   * positives). If the minimum lies in a range of values, the center value is
   * picked up.
   *
   * In a second round of minimization new minimum and maximum bounds are
   * defined based on the center value plus/minus the step (max-min/N) and a
   * new minimization round is restarted for N samples within the new bounds.
   *
   * The procedure continues until all calculated predicates in a given round
   * give the same minimum. At this point, the center threshold is picked up and
   * returned.
   */
  template <typename T> double
    minimizingThreshold(const blitz::Array<double,1>& negatives,
        const blitz::Array<double,1>& positives, T& predicate) {
      const size_t N = 100; ///< number of steps in each iteration
      double min = std::min(blitz::min(negatives), blitz::min(positives));
      double max = std::max(blitz::max(negatives), blitz::max(positives));
      return recursive_minimization(negatives, positives, predicate, min,
          max, N);
    }

  /**
   * Calculates the threshold that is, as close as possible, to the
   * equal-error-rate (EER) given the input data. The EER should be the point
   * where the FAR equals the FRR. Graphically, this would be equivalent to the
   * intersection between the R.O.C. (or D.E.T.) curves and the identity.
   */
  double eerThreshold(const blitz::Array<double,1>& negatives,
      const blitz::Array<double,1>& positives);

  /**
   * Calculates the equal-error-rate (EER) given the input data, on the ROC 
   * Convex Hull, as performed in the Bosaris toolkit.
   * (https://sites.google.com/site/bosaristoolkit/)
   */
  double eerRocch(const blitz::Array<double,1>& negatives,
      const blitz::Array<double,1>& positives);

  /**
   * Calculates the threshold that minimizes the error rate, given the input
   * data. An optional parameter 'cost' determines the relative importance
   * between false-accepts and false-rejections. This number should be between
   * 0 and 1 and will be clipped to those extremes.
   *
   * The value to minimize becomes:
   *
   * ER_cost = [cost * FAR] + [(1-cost) * FRR]
   *
   * The higher the cost, the higher the importance given to *not* making
   * mistakes classifying negatives/noise/impostors.
   */
  double minWeightedErrorRateThreshold(const blitz::Array<double,1>& negatives,
      const blitz::Array<double,1>& positives, double cost);

  /**
   * Calculates the minWeightedErrorRateThreshold() when the cost is 0.5.
   */
  inline double minHterThreshold(const blitz::Array<double,1>& negatives,
      const blitz::Array<double,1>& positives) {
    return minWeightedErrorRateThreshold(negatives, positives, 0.5);
  }

  /**
   * Computes the threshold such that the real FAR is as close as possible
   * to the requested far_value.
   *
   * @param negatives The impostor scores to be used for computing the FAR
   * @param positives The client scores; ignored by this function
   * @param far_value The FAR value where the threshold should be computed
   *
   * @return The computed threshold
   */
  double farThreshold(const blitz::Array<double,1>& negatives,
      const blitz::Array<double,1>& positives, double far_value);

  /**
   * Computes the threshold such that the real FRR is as close as possible
   * to the requested frr_value.
   *
   * @param negatives The impostor scores; ignored by this function
   * @param positives The client scores to be used for computing the FRR
   * @param frr_value The FRR value where the threshold should be computed
   *
   * @return The computed threshold
   */
  double frrThreshold(const blitz::Array<double,1>& negatives,
      const blitz::Array<double,1>& positives, double frr_value);

  /**
   * Calculates the ROC curve given a set of positive and negative scores and a
   * number of desired points. Returns a two-dimensional blitz::Array of
   * doubles that express the X (FRR) and Y (FAR) coordinates in this order.
   * The points in which the ROC curve are calculated are distributed
   * uniformly in the range [min(negatives, positives), max(negatives,
   * positives)].
   */
  blitz::Array<double,2> roc
    (const blitz::Array<double,1>& negatives,
     const blitz::Array<double,1>& positives, size_t points);
     
  /**
   * Calculates the precision-recall curve given a set of positive and negative scores and a
   * number of desired points. Returns a two-dimensional blitz::Array of
   * doubles that express the X (precision) and Y (recall) coordinates in this order.
   * The points in which the curve is calculated are distributed
   * uniformly in the range [min(negatives, positives), max(negatives,
   * positives)].
   */
  blitz::Array<double,2> precision_recall_curve
    (const blitz::Array<double,1>& negatives,
     const blitz::Array<double,1>& positives, size_t points);

  /**
   * Calculates the ROC Convex Hull (ROCCH) given a set of positive and 
   * negative scores and a number of desired points. Returns a 
   * two-dimensional blitz::Array of doubles that contain the coordinates
   * of the vertices of the ROC Convex Hull (the first row is for "pmiss"
   * and the second row is for "pfa").
   * Reference: Bosaris toolkit
   * (https://sites.google.com/site/bosaristoolkit/)
   */
  blitz::Array<double,2> rocch
    (const blitz::Array<double,1>& negatives,
     const blitz::Array<double,1>& positives);

  /**
   * Calculates the Equal Error Rate (EER) on the ROC Convex Hull (ROCCH)
   * from the 2-row matrices containing the pmiss and pfa vectors 
   * (which is the output of the bob::measure::rocch()).
   * Note: pmiss and pfa contain the coordinates of the vertices of the
   *       ROC Convex Hull. 
   * Reference: Bosaris toolkit
   * (https://sites.google.com/site/bosaristoolkit/)
   */
  double rocch2eer(const blitz::Array<double,2>& pmiss_pfa);

  /**
   * Calculates the ROC curve given a set of positive and negative scores at
   * the given FAR coordinates. Returns a two-dimensional blitz::Array of
   * doubles that express the X (FAR) and Y (CAR) coordinates in this order.
   */
  blitz::Array<double,2> roc_for_far(
      const blitz::Array<double,1>& negatives,
      const blitz::Array<double,1>& positives,
      const blitz::Array<double,1>& far_list);

  /**
   * Returns the Deviate Scale equivalent of a false rejection/acceptance
   * ratio.
   *
   * The algorithm that calculates the deviate scale is based on function
   * ppndf() from the NIST package DETware version 2.1, freely available on the
   * internet. Please consult it for more details.
   */
  double ppndf(double value);

  /**
   * Calculates the DET curve given a set of positive and negative scores and a
   * number of desired points. Returns a two-dimensional blitz::Array of
   * doubles that express on its rows:
   *
   * 0: X axis values in the normal deviate scale for the false-rejections
   * 1: Y axis values in the normal deviate scale for the false-accepts
   *
   * You can plot the results using your preferred tool to first create a plot
   * using rows 0 and 1 from the returned value and then place replace the X/Y
   * axis annotation using a pre-determined set of tickmarks as recommended by
   * NIST.
   *
   * The algorithm that calculates the deviate scale is based on function
   * ppndf() from the NIST package DETware version 2.1, freely available on the
   * internet. Please consult it for more details.
   *
   * By 20.04.2011, you could find such package here:
   * http://www.itl.nist.gov/iad/mig/tools/
   */
  blitz::Array<double,2> det
    (const blitz::Array<double,1>& negatives,
     const blitz::Array<double,1>& positives, size_t points);

  /**
   * Calculates the EPC curve given a set of positive and negative scores and a
   * number of desired points. Returns a two-dimensional blitz::Array of
   * doubles that express the X (cost) and Y (HTER on the test set given the
   * min. HTER threshold on the development set) coordinates in this order.
   * Please note that, in order to calculate the EPC curve, one needs two sets
   * of data comprising a development set and a test set. The minimum weighted
   * error is calculated on the development set and then applied to the test
   * set to evaluate the half-total error rate at that position.
   *
   * The EPC curve plots the HTER on the test set for various values of 'cost'.
   * For each value of 'cost', a threshold is found that provides the minimum
   * weighted error (see minWeightedErrorRateThreshold()) on the development
   * set. Each threshold is consecutively applied to the test set and the
   * resulting HTER values are plotted in the EPC.
   *
   * The cost points in which the EPC curve are calculated are distributed
   * uniformly in the range [0.0, 1.0].
   */
  blitz::Array<double,2> epc
    (const blitz::Array<double,1>& dev_negatives,
     const blitz::Array<double,1>& dev_positives,
     const blitz::Array<double,1>& test_negatives,
     const blitz::Array<double,1>& test_positives,
     size_t points);

}}

#endif /* BOB_MEASURE_ERROR_H */
