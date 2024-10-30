function yout = poolDataExpanded(yin,polyorder,forcing,useconstant)
% Copyright 2015, All Rights Reserved
% Code by Steven L. Brunton
% For Paper, "Discovering Governing Equations from Data: 
%        Sparse Identification of Nonlinear Dynamical Systems"
% by S. L. Brunton, J. L. Proctor, and J. N. Kutz

% Modified in 2023 by Andrew Watford

y = [yin forcing];

nVars = size(y, 2);
nObs = size(y,1);

ind = 1;
% poly order 0
if useconstant
    yout(:,ind) = ones(nObs,1);
    ind = ind+1;
end

% poly order 1
for i=1:nVars
    yout(:,ind) = y(:,i);
    ind = ind+1;
end

if(polyorder>=2)
    % poly order 2
    for i=1:nVars
        for j=i:nVars
            yout(:,ind) = y(:,i).*y(:,j);
            ind = ind+1;
        end
    end
end

if(polyorder>=3)
    % poly order 3
    for i=1:nVars
        for j=i:nVars
            for k=j:nVars
                yout(:,ind) = y(:,i).*y(:,j).*y(:,k);
                ind = ind+1;
            end
        end
    end
end

if(polyorder>=4)
    % poly order 4
    for i=1:nVars
        for j=i:nVars
            for k=j:nVars
                for l=k:nVars
                    yout(:,ind) = y(:,i).*y(:,j).*y(:,k).*y(:,l);
                    ind = ind+1;
                end
            end
        end
    end
end

if(polyorder>=5)
    % poly order 5
    for i=1:nVars
        for j=i:nVars
            for k=j:nVars
                for l=k:nVars
                    for i5=l:nVars
                        yout(:,ind) = y(:,i).*y(:,j).*y(:,k).*y(:,l).*y(:,i5);
                        ind = ind+1;
                    end
                end
            end
        end
    end
end

