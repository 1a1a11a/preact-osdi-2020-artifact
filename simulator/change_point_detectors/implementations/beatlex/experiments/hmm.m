function [LL, prior, transmat, mu, Sigma, mixmat, B, path] = learn_hmm(data, numstates)
addpath(genpath('./code/HMMall/'));

prior0 = normalise(rand(numstates,1));
transmat0 = mk_stochastic(rand(numstates, numstates));

[mu_init, Sigma_init] = mixgauss_init(numstates, data, 'diag');

[LL, prior, transmat, mu, Sigma, mixmat] = ...
    mhmm_em(data, prior0, transmat0, mu_init, Sigma_init, [], 'max_iter', 2);
B = mixgauss_prob(data, mu, Sigma, mixmat);
path = viterbi_path(prior, transmat, B);
end
