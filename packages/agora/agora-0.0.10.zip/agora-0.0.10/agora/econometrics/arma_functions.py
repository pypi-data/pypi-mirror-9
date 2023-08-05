###############################################################################
#
#   Agora Portfolio & Risk Management System
#
#   Copyright 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

import numpy as np
import math

__all__= ["AR1", "AR2", "ARMA11", "ARMA21"]


##------------------------------------------------------------------------------
def AR1(x):
    """
    Description:
        ...
    Inputs:
        x - ...
    Returns:
        ...
    """
    lx = np.copy(x[:-1])
    dx = x[1:] - lx
    lx -= lx.mean()

    rho = np.dot(dx, lx) / np.dot(lx, lx)
    res = dx - rho*lx

    # --- slope's standard error
    stderr = math.sqrt(np.dot(res, res) /
                       np.dot(lx, lx) / (len(res) - 1.0))

    return rho, stderr, res


##------------------------------------------------------------------------------
def AR2( x ):
    """
    Description:
        ...
    Inputs:
        x - ...
    Returns:
        ...
    """
    r1, r2 = np.linalg.lstsq(np.vstack([x[1:-1], x[:-2]]).T, x[2:])[0]

    eps = x[2:] - r1*x[1:-1] - r2*x[:-2]

    return r1, r2, eps


##------------------------------------------------------------------------------
def ARMA11(x):
    """
    Description:
        ...
    Inputs:
        x - ...
    Returns:
        ...
    """
    r = np.dot(x[:-1], x[1:]) / np.dot(x[:-1], x[:-1])
    e = x[1:] - r*x[:-1]

    root, phi = np.linalg.lstsq(np.vstack([ x[1:-1], e[:-1]]).T, x[2:])[0]

    eps = x[2:] - root*x[1:-1] - phi*e[:-1]

    return root, phi, eps


##------------------------------------------------------------------------------
def ARMA21(x):
    """
    Description:
        ...
    Inputs:
        x - ...
    Returns:
        ...
    """
    r1, r2 = np.linalg.lstsq(np.vstack([x[1:-1], x[:-2]]).T, x[2:])[0]

    e = x[2:] - r1*x[1:-1] -r2*x[:-2]

    r1, r2, phi = np.linalg.lstsq(np.vstack([x[2:-1],
                                             x[1:-2], e[:-1]]).T, x[3:])[0]

    eps = x[3:] - r1*x[2:-1] - r2*x[1:-2] - phi*e[:-1]

    return r1, r2, phi, eps


##------------------------------------------------------------------------------
if __name__ == "__main__":
    import pylab

    def generate_AR1(root, x0, eps):
        x = x0
        yield x
        for e in eps:
            x = root*x + e
            yield x

    root = 0.99
    ndays = 150
    nsims = 20000

    err = np.random.randn(ndays - 1)
    ar1 = np.fromiter(generate_AR1(root, 0.0, err), np.double, ndays)

    rho, stderr, res = AR1(ar1)

    # --- standardize residuals
    res -= res.mean()
    res /= res.std()

    root = rho + 1.0

    roots = []
    for k in range(nsims):
        idx = np.random.randint(0, ndays - 1, ndays - 1)
        ar1 = np.fromiter(generate_AR1(root, ar1[0], res[idx]), np.double, ndays)
        rho, _, _ = AR1(ar1)
        roots.append(rho + 1.0)

    print(root, np.mean(roots), np.median(roots), np.percentile(roots, 99))

    pylab.hist(roots, 200)
    pylab.show()
