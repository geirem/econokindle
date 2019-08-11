# Security Status and Development

## General
The application fetches data directly from the Economist (and no other sources), using a verified TLS connection.  The
likelyhood of any malicious code being processed by this application is therefore small.  

The fetched content is
processed using `json.loads()` and [JsonPath RW](https://github.com/kennknowles/python-jsonpath-rw).

## Bug Hunting / Code Review
#### OWASP Dependency Check
Dependencies used by the application are scanned for known vulnerabilities using the
[OWASP Dependency Checker](https://jeremylong.github.io/DependencyCheck/analyzers/python.html).  It currently requires the 
[NIST Data Mirror](https://github.com/stevespringett/nist-data-mirror/).  

I am running the mirror at _http://localhost:8080/_, and scan with the full string:
```bash
dependency-check \
-d $(pwd)/owasp -c 2 --project EconoKindle -s . --enableExperimental \
--cveUrl12Modified=http://localhost:8080/nvdcve-modified.xml.gz \
--cveUrl20Modified=http://localhost:8080/nvdcve-2.0-modified.xml.gz \
--cveUrl12Base=http://localhost:8080/nvdcve-%d.xml.gz \
--cveUrl20Base=http://localhost:8080/nvdcve-2.0-%d.xml.gz \
--log verbose.log
```

#### SonarCloud SAST
SonarCloud status is available in https://sonarcloud.io/dashboard?id=geirem_econokindle.  Realtime
feedback is provided in IntelliJ IDEA using the [SonarLint](https://www.sonarlint.org/intellij/) plugin.

## Reporting a Bug

Security bugs can be reported on the https://github.com/geirem/econokindle GitHub _security_ tab.  All reports are considered, and
if severe enough, I'll write a patch or workaround in quickly - no guarantees, though.  Also,
consider a PR with an appropriate fix.

Report security bugs in third-party modules to the person or team maintaining
the module.

## Disclosure Policy

Reported bugs are handled using the GitHub features.  If appropriate, a commit will
describe the gist of the vulnerability, and the intended solution.  Attribution
is included, if requested by the reporter.
