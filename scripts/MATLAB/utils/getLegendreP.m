function P = getLegendreP(d, r)
    P = zeros(d, r);
    x = linspace(-1, 1, d);
    for k=1:r
        n = k-1;
        P(:, k) = legendreP(n, x);
        normalization = norm(P(:, k));
        P(:, k) = P(:, k) ./ normalization;
    end
end