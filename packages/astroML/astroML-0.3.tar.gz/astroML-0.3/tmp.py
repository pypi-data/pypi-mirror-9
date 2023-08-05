import numpy as np
import pymc

print("pymc version", pymc.__version__)

np.random.seed(0)


xi = np.random.random(10)
dyi = np.random.random(10)
yi = np.random.normal(2 * xi, dyi)

# We're doing a linear fit with a background. Pb is the nuisance parameter
# which specifies the probability that points are drawn from a normal
# distribution N(Yb, sigmab^2).

# uniform prior on Pb, the fraction of bad points
Pb = pymc.Uniform('Pb', 0, 1.0, value=0.1)

# uniform prior on Yb, the centroid of the outlier distribution
Yb = pymc.Uniform('Yb', -10000, 10000, value=0)

# uniform prior on log(sigmab), the spread of the outlier distribution
log_sigmab = pymc.Uniform('log_sigmab', -10, 10, value=5)

# define priors on beta = (slope, intercept)
@pymc.stochastic
def beta_M1(value=np.array([2., 100.])):
    """Slope and intercept parameters for a straight line.
    The likelihood corresponds to the prior probability of the parameters."""
    slope, intercept = value
    prob_intercept = 1 + 0 * intercept
    # uniform prior on theta = arctan(slope)
    # d[arctan(x)]/dx = 1 / (1 + x^2)
    prob_slope = np.log(1. / (1. + slope ** 2))
    return prob_intercept + prob_slope


@pymc.deterministic
def model_M1(xi=xi, beta=beta_M1):
    slope, intercept = beta
    return slope * xi + intercept


@pymc.deterministic
def sigmab(log_sigmab=log_sigmab):
    return np.exp(log_sigmab)


# set up the expression for likelihood
def mixture_likelihood(yi, model, dyi, Pb, Yb, sigmab):
    if (Pb < 0) or (Pb > 1):
        print("error: Pb =", Pb)
        raise ValueError("Pb out of range")

    Vi = dyi ** 2
    Vb = sigmab ** 2

    root2pi = np.sqrt(2 * np.pi)

    L_in = (1. / root2pi / dyi
            * np.exp(-0.5 * (yi - model) ** 2 / Vi))

    L_out = (1. / root2pi / np.sqrt(Vi + Vb)
             * np.exp(-0.5 * (yi - Yb) ** 2 / (Vi + Vb)))

    return np.sum(np.log((1 - Pb) * L_in + Pb * L_out))

MixtureNormal = pymc.stochastic_from_dist('mixturenormal',
                                          logp=mixture_likelihood,
                                          dtype=np.float,
                                          mv=True)

y_mixture = MixtureNormal('y_mixture', model=model_M1, dyi=dyi,
                          Pb=Pb, Yb=Yb, sigmab=sigmab,
                          observed=True, value=yi)

M = dict(y_mixture=y_mixture, beta_M1=beta_M1, model_M1=model_M1,
         Pb=Pb, Yb=Yb, log_sigmab=log_sigmab, sigmab=sigmab)

S = pymc.MCMC(M)
S.sample(iter=25000, burn=5000)
