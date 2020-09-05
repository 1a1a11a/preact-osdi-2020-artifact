% Learns Gaussian HMM parameters from a single data sequence. 
% Inputs: data (a single vector of Gaussian outputs); numstates (number of
% states to learn)
% Outputs: see "help mhmm_em". The outputs are: LL (log likelihood), prior (prior for
% states), transmat (transition matrix), mu (means given each state), Sigma
% (variance given each state), mixmat (ignore this), B (probability of each
% state at each time), path (most likely set of states). 

function [LL, prior, transmat, mu, Sigma, mixmat, B, path] = learn_hmm(data, numstates)
addpath(genpath('HMMall'));

prior0 = normalise(rand(numstates,1));
transmat0 = mk_stochastic(rand(numstates, numstates));

[mu_init, Sigma_init] = mixgauss_init(numstates, data, 'diag');

[LL, prior, transmat, mu, Sigma, mixmat] = ...
    mhmm_em(data, prior0, transmat0, mu_init, Sigma_init, [], 'max_iter', 2);
B = mixgauss_prob(data, mu, Sigma, mixmat);
path = viterbi_path(prior, transmat, B);
rmpath(genpath('HMMall'));
end
