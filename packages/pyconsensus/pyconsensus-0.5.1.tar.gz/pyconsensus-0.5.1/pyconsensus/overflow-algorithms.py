        elif self.algorithm == "fixed-var-length":
            U, Sigma, Vt = np.linalg.svd(covariance_matrix)
            variance_explained = np.cumsum(Sigma / np.trace(covariance_matrix))
            length = 0
            for i, var_exp in enumerate(variance_explained):
                loading = U.T[i]
                score = Sigma[i] * np.dot(mean_deviation, loading)
                length += score**2
                if var_exp > self.variance_threshold: break
            self.num_components = i
            length = np.sqrt(length)
            nc = self.nonconformity(length, reports_filled)

        elif self.algorithm == "ica-adjusted":
            ica = FastICA(n_components=self.num_events, whiten=False)
            while not convergence:
                with warnings.catch_warnings(record=True) as w:
                    try:
                        S_ = ica.fit_transform(covariance_matrix)   # Reconstruct signals
                        if len(w):
                            continue
                        else:
                            first_loading = S_[:,0]
                            first_loading /= np.sqrt(np.sum(first_loading**2))
                            first_score = np.array(np.dot(mean_deviation, first_loading)).ravel()
                            nc = self.nonconformity(first_score, reports_filled)
                            self.convergence = not any(np.isnan(nc))
                    except:
                        continue

        elif self.algorithm == "ica-prewhitened":
            ica = FastICA(n_components=self.num_events, whiten=True)
            while not convergence:
                with warnings.catch_warnings(record=True) as w:
                    try:
                        S_ = ica.fit_transform(covariance_matrix)   # Reconstruct signals
                        if len(w):
                            continue
                        else:
                            first_loading = S_[:,0]
                            first_loading /= np.sqrt(np.sum(first_loading**2))
                            first_score = np.array(np.dot(mean_deviation, first_loading)).ravel()
                            nc = self.nonconformity(first_score, reports_filled)
                            self.convergence = not any(np.isnan(nc))
                    except:
                        continue

        elif self.algorithm == "ica-inverse":
            ica = FastICA(n_components=self.num_events, whiten=True)
            while not convergence:
                with warnings.catch_warnings(record=True) as w:
                    try:
                        S_ = ica.fit_transform(covariance_matrix)
                        if len(w):
                            continue
                        else:
                            first_loading = S_[:,0]
                            first_loading /= np.sqrt(np.sum(first_loading**2))
                            first_score = np.array(np.dot(mean_deviation, first_loading)).ravel()
                            nc = 1 / np.abs(first_score)
                            nc /= np.sum(nc)
                            self.convergence = not any(np.isnan(nc))
                    except:
                        continue

        # Brute force scoring: replicated rows
        elif self.algorithm == "covariance-replicate":
            B = []
            for i in range(self.num_reporters):
                for j in range(self.reptokens[i]):
                    B.append(reports_filled[i,:].tolist())
            num_rows = len(B)
            B = np.array(B)
            row_mean = np.mean(B, axis=1)
            centered = np.zeros(B.shape)
            onesvect = np.ones(self.num_events)
            for i in range(num_rows):
                centered[i,:] = B[i,:] - onesvect * row_mean[i]
            covmat = np.dot(centered, centered.T) / self.num_events
            # Sum across columns of the (other) covariance matrix
            contrib_rpl = np.sum(covmat, 1)
            # relative_contrib_rpl = contrib_rpl / np.sum(contrib_rpl)
            relative_contrib = np.zeros(self.num_reporters)
            row = 0
            for i in range(self.num_reporters):
                relative_contrib[i] = self.reptokens[i] * contrib_rpl[row]
                # relative_contrib[i] = contrib_rpl[row] # same result as "covariance"
                row += self.reptokens[i]
            relative_contrib /= np.sum(relative_contrib)
            nc = self.nonconformity(relative_contrib, reports_filled)            
