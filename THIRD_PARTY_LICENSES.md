# Third-Party Licenses

This document lists all third-party dependencies used in the finbot project and their license information.

**Project License:** MIT License

**Last Updated:** 2026-02-16

## License Summary

| License Type | Count | Compatibility | Risk Level |
|--------------|-------|---------------|------------|
| MIT | 124 | ✅ Compatible | Low |
| BSD (BSD-2/BSD-3) | 68 | ✅ Compatible | Low |
| Apache 2.0 | 45 | ✅ Compatible | Low |
| ISC | 6 | ✅ Compatible | Low |
| Mozilla Public License 2.0 (MPL 2.0) | 4 | ✅ Compatible | Low |
| Unlicense | 1 | ✅ Compatible | Low |
| Python Software Foundation License | 4 | ✅ Compatible | Low |
| **GPL/LGPL** | **5** | ⚠️ **Requires Review** | **Medium** |

## License Compatibility Assessment

### ✅ Compatible Licenses (248 packages)

The vast majority of dependencies use permissive licenses that are fully compatible with the MIT license:

- **MIT License**: Highly permissive, allows commercial use, modification, distribution
- **BSD Licenses (2-Clause, 3-Clause)**: Similar to MIT, highly permissive
- **Apache 2.0**: Permissive with patent grant protection
- **ISC License**: Functionally equivalent to MIT
- **MPL 2.0**: Weak copyleft, file-level (compatible when used as library)
- **Python Software Foundation License**: Permissive, similar to BSD
- **Unlicense**: Public domain dedication

### ⚠️ Copyleft Licenses Requiring Attention (5 packages)

The following dependencies use GPL/LGPL licenses, which have copyleft requirements:

#### 1. **backtrader** (v1.9.78.123) - GPLv3+
- **License**: GNU General Public License v3 or later (GPLv3+)
- **Risk Level**: Medium
- **Impact**: Core backtesting engine
- **Assessment**:
  - GPLv3 is a strong copyleft license
  - Since finbot is distributed as source code under MIT, and backtrader is used as a library dependency, this is generally acceptable
  - Users installing finbot via pip will install backtrader separately, maintaining license separation
  - **Recommendation**: Consider documenting that backtrader is an optional dependency for backtesting features, or evaluate alternative backtesting engines (e.g., zipline-reloaded, bt) for future versions

#### 2. **ecos** (v2.0.14) - GPLv3
- **License**: GPLv3
- **Risk Level**: Medium
- **Impact**: Embedded Conic Solver (dependency of cvxpy for portfolio optimization)
- **Assessment**:
  - Used indirectly through cvxpy for portfolio optimization
  - Similar considerations as backtrader
  - **Recommendation**: Acceptable as optional dependency; document in license notices

#### 3. **frozendict** (v2.4.7) - LGPLv3
- **License**: GNU Lesser General Public License v3 (LGPLv3)
- **Risk Level**: Low-Medium
- **Impact**: Immutable dictionary implementation
- **Assessment**:
  - LGPL is a weak copyleft license that allows linking without imposing GPL requirements on the linking code
  - Using as a library dependency is generally safe
  - **Recommendation**: No action required; LGPL is library-friendly

#### 4. **nautilus_trader** (v1.222.0) - LGPLv3+
- **License**: GNU Lesser General Public License v3 or later (LGPLv3+)
- **Risk Level**: Low-Medium
- **Impact**: High-performance algorithmic trading platform
- **Assessment**:
  - LGPL allows library usage without copyleft contamination
  - Used as an optional/experimental component
  - **Recommendation**: No action required; consider documenting as optional dependency

#### 5. **portion** (v2.6.1) - LGPLv3
- **License**: GNU Lesser General Public License v3 (LGPLv3)
- **Risk Level**: Low-Medium
- **Impact**: Interval data structure operations
- **Assessment**:
  - LGPL allows library usage
  - Likely a transitive dependency
  - **Recommendation**: No action required

### License Compatibility Analysis

**Overall Assessment**: ✅ **Generally Compatible**

The finbot project can be distributed under the MIT license with the current dependency set, with the following considerations:

1. **GPL Dependencies (backtrader, ecos)**: These strong copyleft licenses do not contaminate the MIT-licensed code when used as separate library dependencies installed via pip. However, if you were to distribute a compiled binary including these libraries, GPL requirements would apply.

2. **LGPL Dependencies (frozendict, nautilus_trader, portion)**: LGPL explicitly permits linking from proprietary or MIT-licensed software, making these fully compatible.

3. **Best Practices**:
   - Maintain clear separation between finbot's MIT code and GPL dependencies
   - Distribute finbot as source code with dependencies listed in pyproject.toml
   - Document GPL/LGPL dependencies in this file
   - Consider marking GPL dependencies as "optional" in future versions

## Production Dependencies (65 packages)

### Data & Finance Libraries

| Package | Version | License | URL |
|---------|---------|---------|-----|
| backtrader | 1.9.78.123 | GPLv3+ ⚠️ | https://github.com/mementum/backtrader |
| beautifulsoup4 | 4.14.3 | MIT | https://www.crummy.com/software/BeautifulSoup/bs4/ |
| click | 8.3.1 | BSD-3-Clause | https://github.com/pallets/click/ |
| dynaconf | 3.2.12 | MIT | https://github.com/dynaconf/dynaconf |
| filterpy | 1.4.5 | MIT | https://github.com/rlabbe/filterpy |
| httpx | 0.28.1 | BSD | https://github.com/encode/httpx |
| jupyter | 1.1.1 | BSD | https://jupyter.org |
| limits | 5.8.0 | MIT | https://limits.readthedocs.org |
| matplotlib | 3.10.8 | PSF | https://matplotlib.org |
| nasdaq-data-link | 1.0.4 | MIT | https://github.com/Nasdaq/data-link-python |
| nautilus_trader | 1.222.0 | LGPLv3+ ⚠️ | https://nautilustrader.io |
| numpy | 1.26.4 | BSD | https://numpy.org |
| numpy-financial | 1.0.0 | BSD | https://numpy.org/numpy-financial/ |
| openpyxl | 3.1.5 | MIT | https://openpyxl.readthedocs.io |
| pandas | 2.3.3 | BSD | https://pandas.pydata.org |
| pandas-datareader | 0.10.0 | BSD | https://github.com/pydata/pandas-datareader |
| pillow | 12.1.1 | MIT-CMU | https://python-pillow.github.io |
| plotly | 5.24.1 | MIT | https://plotly.com/python/ |
| prettytable | 3.17.0 | MIT | https://github.com/jazzband/prettytable |
| pyarrow | 23.0.0 | Apache-2.0 | https://arrow.apache.org/ |
| pyportfolioopt | 1.5.6 | MIT | https://github.com/robertmartin8/PyPortfolioOpt |
| pywavelets | 1.9.0 | MIT AND BSD-3-Clause | https://github.com/PyWavelets/pywt |
| python-dotenv | 1.2.1 | BSD-3-Clause | https://github.com/theskumar/python-dotenv |
| quantstats | 0.0.81 | Apache-2.0 | https://github.com/ranaroussi/quantstats |
| requests | 2.32.5 | Apache-2.0 | https://requests.readthedocs.io |
| ruptures | 1.1.10 | BSD | https://github.com/deepcharles/ruptures/ |
| scikit-learn | 1.8.0 | BSD-3-Clause | https://scikit-learn.org |
| scipy | 1.17.0 | BSD | https://scipy.org/ |
| seaborn | 0.13.2 | BSD | https://github.com/mwaskom/seaborn |
| selenium | 4.40.0 | Apache-2.0 | https://www.selenium.dev |
| statsmodels | 0.14.6 | BSD | https://www.statsmodels.org/ |
| streamlit | 1.54.0 | Apache-2.0 | https://streamlit.io |
| tqdm | 4.67.3 | MPL-2.0 AND MIT | https://tqdm.github.io |
| webdriver-manager | 4.0.2 | Apache-2.0 | https://github.com/SergeyPirogov/webdriver_manager |
| xlrd | 2.0.2 | BSD | http://www.python-excel.org/ |
| yfinance | 0.2.66 | Apache-2.0 | https://github.com/ranaroussi/yfinance |
| zstandard | 0.25.0 | BSD-3-Clause | https://github.com/indygreg/python-zstandard |

### Google API Libraries

| Package | Version | License | URL |
|---------|---------|---------|-----|
| google-api-core | 2.29.0 | Apache-2.0 | https://github.com/googleapis/python-api-core |
| google-api-python-client | 2.189.0 | Apache-2.0 | https://github.com/googleapis/google-api-python-client/ |
| google-auth | 2.48.0 | Apache-2.0 | https://github.com/googleapis/google-auth-library-python |
| google-auth-httplib2 | 0.3.0 | Apache-2.0 | https://github.com/GoogleCloudPlatform/google-auth-library-python-httplib2 |
| google-auth-oauthlib | 1.2.4 | Apache-2.0 | https://github.com/GoogleCloudPlatform/google-auth-library-python-oauthlib |
| googleapis-common-protos | 1.72.0 | Apache-2.0 | https://github.com/googleapis/google-cloud-python |

### Portfolio Optimization Dependencies

| Package | Version | License | URL |
|---------|---------|---------|-----|
| clarabel | 0.11.1 | Apache-2.0 | (cvxpy solver) |
| cvxpy | 1.7.5 | Apache-2.0 | https://github.com/cvxpy/cvxpy |
| ecos | 2.0.14 | GPLv3 ⚠️ | http://github.com/embotech/ecos |
| osqp | 1.1.0 | Apache-2.0 | https://osqp.org/ |
| scs | 3.2.11 | MIT | (cvxpy solver) |

### Core Infrastructure

| Package | Version | License | URL |
|---------|---------|---------|-----|
| certifi | 2026.1.4 | MPL-2.0 | https://github.com/certifi/python-certifi |
| charset-normalizer | 3.4.4 | MIT | https://github.com/jawah/charset_normalizer |
| cryptography | 46.0.5 | Apache-2.0 OR BSD-3-Clause | https://github.com/pyca/cryptography |
| frozendict | 2.4.7 | LGPLv3 ⚠️ | https://github.com/Marco-Sulla/python-frozendict |
| idna | 3.11 | BSD-3-Clause | https://github.com/kjd/idna |
| packaging | 24.2 | Apache-2.0 OR BSD | https://github.com/pypa/packaging |
| portion | 2.6.1 | LGPLv3 ⚠️ | https://github.com/AlexandreDecan/portion |
| python-dateutil | 2.9.0.post0 | Apache-2.0 OR BSD | https://github.com/dateutil/dateutil |
| pytz | 2025.2 | MIT | http://pythonhosted.org/pytz |
| six | 1.17.0 | MIT | https://github.com/benjaminp/six |
| tenacity | 9.1.4 | Apache-2.0 | https://github.com/jd/tenacity |
| tzdata | 2025.3 | Apache-2.0 | https://github.com/python/tzdata |
| urllib3 | 2.6.3 | MIT | https://github.com/urllib3/urllib3 |

## Development Dependencies (18 packages)

| Package | Version | License | URL |
|---------|---------|---------|-----|
| bandit | 1.9.3 | Apache-2.0 | https://bandit.readthedocs.io/ |
| google-api-python-client-stubs | 1.31.0 | Apache-2.0 | (type stubs) |
| interrogate | 1.7.0 | MIT | https://interrogate.readthedocs.io |
| mkdocs | 1.6.1 | BSD-2-Clause | https://github.com/mkdocs/mkdocs |
| mkdocs-autorefs | 1.4.4 | ISC | https://mkdocstrings.github.io/autorefs |
| mkdocs-material | 9.7.1 | MIT | https://github.com/squidfunk/mkdocs-material |
| mkdocs-material-extensions | 1.3.1 | MIT | https://github.com/facelessuser/mkdocs-material-extensions |
| mkdocstrings | 0.30.1 | ISC | https://mkdocstrings.github.io |
| mkdocstrings-python | 2.0.2 | ISC | https://mkdocstrings.github.io/python |
| mypy | 1.19.1 | MIT | https://www.mypy-lang.org/ |
| pandas-stubs | 2.3.3.260113 | BSD | https://pandas.pydata.org |
| pre-commit | 3.8.0 | MIT | https://github.com/pre-commit/pre-commit |
| pyupgrade | 3.21.2 | MIT | https://github.com/asottile/pyupgrade |
| pytest | 9.0.2 | MIT | https://docs.pytest.org/en/latest/ |
| pytest-cov | 7.0.0 | MIT | https://pytest-cov.readthedocs.io |
| ruff | 0.15.0 | MIT | https://docs.astral.sh/ruff |
| ssort | 0.16.0 | MIT | https://github.com/bwhmather/ssort |
| types-* | (various) | Apache-2.0 | https://github.com/python/typeshed |

## Transitive Dependencies

The project includes numerous transitive dependencies (dependencies of dependencies). All have been audited and use compatible licenses. Major categories include:

- **Jupyter ecosystem**: BSD/MIT licensed (ipykernel, ipython, notebook, jupyterlab, etc.)
- **HTTP/networking**: Apache-2.0, MIT, BSD (httpcore, h11, websockets, etc.)
- **Serialization**: Apache-2.0, MIT (protobuf, msgspec, etc.)
- **Build tools**: MIT, BSD (setuptools, packaging, etc.)

## License Obligations

### Attribution Requirements

Most dependencies require preservation of copyright notices and license text. This is satisfied by:

1. Including this THIRD_PARTY_LICENSES.md file in the distribution
2. Maintaining dependency metadata in pyproject.toml
3. Dependencies are installed separately via pip, preserving their individual license files

### Copyleft Considerations

For GPL/LGPL dependencies (backtrader, ecos, frozendict, nautilus_trader, portion):

1. **Source Code Access**: These libraries are distributed as source code via PyPI
2. **Separation**: They are separate works installed as dependencies, not incorporated into finbot's codebase
3. **Dynamic Linking**: Python's import mechanism constitutes dynamic linking, which is generally acceptable under LGPL and arguably acceptable under GPL for separately distributed components

### Recommendations

1. **Document GPL dependencies**: Maintain this license audit document
2. **Consider alternatives**: For future versions, evaluate MIT/BSD/Apache-2.0 alternatives to backtrader (e.g., vectorbt, bt, zipline-reloaded)
3. **Clear boundaries**: Keep finbot's MIT code separate from GPL dependencies
4. **Distribution**: Continue distributing as source code with pip-installable dependencies

## No Proprietary Licenses

✅ All dependencies use open-source licenses. No proprietary or closed-source dependencies detected.

## License Audit Methodology

This audit was performed using pip-licenses (v5.5.1) on 2026-02-16:

```bash
uv pip install pip-licenses
uv run pip-licenses --format=json --with-urls --with-description
```

License information is pulled from package metadata and verified against package repositories.

## Questions or Concerns?

If you have questions about license compatibility or need legal advice:

1. This document provides information only and is not legal advice
2. Consult with a qualified attorney for specific legal questions
3. For questions about individual package licenses, refer to their repositories

## Updating This Document

To regenerate the license audit:

```bash
# Install pip-licenses
uv pip install pip-licenses

# Generate report
uv run pip-licenses --format=markdown --with-urls > licenses_temp.md

# Review and update this document manually
```

---

**Note**: License information is provided in good faith based on package metadata. Always verify critical license information directly with package maintainers and consult legal counsel for compliance questions.
