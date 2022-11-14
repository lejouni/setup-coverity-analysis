# setup-coverity-analysis
This will setup the Coverity Analysis tools into PATH. It will download the given version from given Coverity Connect instance. Will extract the coverity tar -file into given location. This location can be added to cache for example.

## Available Options
| Option name | Description | Default value | Required |
|----------|----------|---------|----------|
| log_level | Logging level | DEBUG | false |
| project | Project name in Coverity Connect, if not given then default=github.repository | ${{github.repository}} | false |
| stream | Project stream name in Coverity Connect, if not given then default=github.ref_name | ${{github.ref_name}} | false |
| cov_version | What version of Coverity Analysis is needed, example: cov-analysis-linux64-2022.6.1 | cov-analysis-linux64-2022.6.1 | false |
| cov_url | URL for Coverity Connect where the analysis tar file can be downloaded | - | true |
| cov_username | Coverity Connect username | - | true |
| cov_password | Coverity Connect password | - | true |
| cov_license | Path to the license file. License is needed for analysis. If license file is not given, then it will be downloaded from the Coverity Connect Downloads. | - | false |
| cov_install_folder | To which folder the Coverity tools are extracted | /tmp/cache/coverity | false |
| cov_remove_folders | With this you can give space separated list of folders which you will not need from Coverity Analysis and that way safe some space. (by default are removed architecture-analysis sdk dynamic-analysis forcheck doc) | architecture-analysis sdk dynamic-analysis forcheck doc | false |
| cov_configures | With this you can configure Coverity Analysis. (by default cov-configure --java && cov-configure --javascript && cov-configure --python && cov-configure --kotlin && cov-configure --gcc --xml-option=prepend_arg:--ppp_translator --xml-option=prepend_arg:"replace/#\s*error \"Do not include _sd-common.h directly; it is a private header.\"/" && cov-configure --template --compiler c++ --comptype gcc && cov-configure --template --compiler cc --comptype gcc) | cov-configure --java && cov-configure --javascript && cov-configure --python && cov-configure --kotlin && cov-configure --gcc --xml-option=prepend_arg:--ppp_translator --xml-option=prepend_arg:"replace/#\s*error \"Do not include _sd-common.h directly; it is a private header.\"/" && cov-configure --template --compiler c++ --comptype gcc && cov-configure --template --compiler cc --comptype gcc | false |
| cov_intermediate_dir | Intermediate directory | ${{github.workspace}}/idir | false |
| cov_output_format | With this you can specify that do you want to have output as a json, sarif or html format. If not given, then no output file created. Options are json, sarif or html. | - | false |
| cov_output | What is wanted as an output. Html case, output must be folder with fullpath where you want to html report to be created, json case outoput must be json file with full path and sarif case it must be sarif file with full path. | - | false |
| cache | Coverity tools and Intermediate directory can be cached. Options are coverity, idir and all. Coverity will only cache Coverity tools, idir will cache only intermediate dir and all will cache both. The cache for intermediate directory is set only for current day. The cache for Coverity tools are set for the Coverity version. The coverity cache will stay active if it is used within a week, otherwise it will be deleted automatically. | - | false |
| create_if_not_exists | Create project and stream if they do not exists | false | false |

## Values which will be set into environment variables

These key-value pairs are set into environment values and are accessed with **${{env.key}}**
| Key | Value |
|----------|--------|
| project | Given project name or ${{github.repository}}. Will replace special characters "\/ %&" with "-". Example: Organiztion/projectName -> Organization-projectName.|
| stream | project-given stream name or ${{github.ref_name}}. Will replace special characters "\/ %&" with "-". Example: Organization-projectName-main |
| cov_url | ${{inputs.cov_url}} |
| cov_username | ${{inputs.cov_username}} |
| cov_password | ${{inputs.cov_password}} |
| cov_install_folder | ${{inputs.cov_install_folder}} |
| cov_intermediate_dir | ${{inputs.cov_intermediate_dir}} |
| cov_output_format | ${{inputs.cov_output_format}} |
| cov_output | ${{inputs.cov_output}} |

## Usage

**Example full pipeline:**
```yaml
name: Java CI with Maven and Coverity

on:
  push:
    branches: [ main ]
  pull_request:
    branches:
      - "main"

jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3 # This will checkout the source codes from repository

    - name: Set up JDK 1.11 # This will add Java into the runners PATH
      uses: actions/setup-java@v3.6.0
      with:
        java-version: '11'
        distribution: 'temurin'
        cache: 'maven' # Cache maven modules

    - name: Set up Coverity # This will add Coverity Analysis tools into runner PATH
      uses: lejouni/setup-coverity-analysis@v2.8.18
      with:
        cov_version: cov-analysis-linux64-2022.6.1
        cov_url: ${{secrets.COVERITY_SERVER_URL}}
        cov_license: ${{github.workspace}}/scripts/license.dat
        cov_username: ${{secrets.COVERITY_USERNAME}}
        cov_password: ${{secrets.COVERITY_ACCESS_TOKEN}}
        cov_output_format: sarif #Optional, but if given the options are html, json and sarif
        cov_output: ${{github.workspace}}/coverity_results.sarif.json
        create_if_not_exists: true # will create project and stream if they don't exists yet
        cache: coverity # Optional, but if given the options are coverity, idir and all

    - if: ${{github.event_name == 'pull_request'}}
      name: Build with Maven and Full Analyze with Coverity # This will run the full Coverity Analsysis
      uses: lejouni/coverity-buildless-analysis@v2.8.28
      with:
        cov_capture_mode: project # Options are project, scm, source (default) and config

    - if: ${{github.event_name == 'push'}}
      name: Build with Maven and Incremental Analyze with Coverity # This will run the incremental Coverity Analsysis
      uses: lejouni/coverity-buildless-analysis@v2.8.28
      with:
        cov_capture_mode: project # Options are project, scm, source (default) and config
        cov_analysis_mode: incremental # Optional, but options are full (default) or incremental
        github_access_token: ${{secrets.ACCESS_TOKEN_GITHUB}} # this is required in incremental mode, used to get changed files via Github API

    - name: Upload SARIF file
      uses: github/codeql-action/upload-sarif@v2
      with:
        # Path to SARIF file
        sarif_file: ${{github.workspace}}/coverity_results.sarif.json
      continue-on-error: true

    - name: Archive scanning results
      uses: actions/upload-artifact@v3
      with:
        name: coverity-scan-results
        path: ${{github.workspace}}/coverity_results.sarif.json
      continue-on-error: true
```

**Setup part:**
```yaml
    - name: Set up Coverity # This will add Coverity Analysis tools into runner PATH
      uses: lejouni/setup-coverity-analysis@v2.8.18
      with:
        cov_version: cov-analysis-linux64-2022.6.1
        cov_url: ${{secrets.COVERITY_SERVER_URL}}
        cov_license: ${{github.workspace}}/scripts/license.dat
        cov_username: ${{secrets.COVERITY_USERNAME}}
        cov_password: ${{secrets.COVERITY_ACCESS_TOKEN}}
        cov_output_format: sarif #Optional, but if given the options are html, json and sarif
        cov_output: ${{github.workspace}}/coverity_results.sarif.json
        create_if_not_exists: true # will create project and stream if they don't exists yet
        cache: coverity # Optional, but if given the options are coverity, idir and all
```

**Buildless analysis with [lejouni/coverity-buildless-analysis](https://github.com/lejouni/coverity-buildless-analysis)**

Prerequisite is that lejouni/setup-coverity-analysis -action is executed first or Coverity tools are installed into the runner PATH in some other way.

Lejouni/coverity-buildless-analysis -action is utilizing those environment variables set by this setup -action.
```yaml
    - if: ${{github.event_name == 'pull_request'}}
      name: Build with Maven and Full Analyze with Coverity # This will run the full Coverity Analsysis
      uses: lejouni/coverity-buildless-analysis@v2.8.28
      with:
        cov_capture_mode: project # Options are project, scm, source (default) and config

    - if: ${{github.event_name == 'push'}}
      name: Build with Maven and Incremental Analyze with Coverity # This will run the incremental Coverity Analsysis
      uses: lejouni/coverity-buildless-analysis@v2.8.28
      with:
        cov_capture_mode: project # Options are project, scm, source (default) and config
        cov_analysis_mode: incremental # Optional, but options are full (default) or incremental
        github_access_token: ${{secrets.ACCESS_TOKEN_GITHUB}} # this is required in incremental mode, used to get changed files via Github API
```

**Build analysis with [lejouni/coverity-build-analysis](https://github.com/lejouni/coverity-build-analysis)**

If you need to run build command in oder to build your application like in C/C++, then you must use this action.

Prerequisite is that lejouni/setup-coverity-analysis -action is executed first or Coverity tools are installed into the runner PATH in some other way.

Lejouni/coverity-build-analysis -action is utilizing those environment variables set by this setup -action.
```yaml
    - if: ${{github.event_name == 'pull_request'}}
      name: Build with Maven and Full Analyze with Coverity # This will run the full Coverity Analsysis
      uses: lejouni/coverity-build-analysis@v4.3.3
      with:
        build_command: mvn -B package --file pom.xml # Used build command must be given.
    - if: ${{github.event_name == 'push'}}
      name: Build with Maven and Incremental Analyze with Coverity # This will run the incremental Coverity Analsysis
      uses: lejouni/coverity-build-analysis@v4.3.3
      with:
        build_command: mvn -B package --file pom.xml # Used build command must be given.
        cov_analysis_mode: incremental # Optional, but options are full (default) or incremental
        github_access_token: ${{secrets.ACCESS_TOKEN_GITHUB}} # this is required in incremental mode, used to get changed files via Github API
```