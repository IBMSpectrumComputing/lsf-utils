# bsubkill

bsubkill is a wrapper of bkill. It allows a user to kill another user's job.

If you would like to contribute, you must follow the DCO process in the attached [DCO Readme file](https://github.com/IBMSpectrumComputing/lsf-utils/blob/master/IBMDCO.md) in the root of this repository.  It essentially requires you to provide a Sign Off line in the notes of your pull request stating that the work does not infinge on the work of others. For more details, refer to the DCO Readme file.

## Release Information

* IBM Spectrum LSF bsubkill
* Supporting LSF Release: 10.1
* Version: 1.0
* Publication date: 25 Feb 2026
* Last modified: 25 Feb 2026

## Introduction

You might want to kill a job that was submitted using bsubmit for a different user. 

To do this, this package introduces a bkill wrapper with the setuid bit set. The wrapper retrieves the user of the job id and verifies if the mapping is valid using a configuration file. 

## Building and installing

Before building, set the LSF environment variables:

    $ source profile.lsf

To build and install, go to the main source directory and run the following commands:

    $ make
    $ make install

A new executable file named bsubkill is installed in the $LSF_BINDIR directory. Ensure that the file is owned by root and has the setuid bit enabled. To do this, you must have root privileges.

## Configuring and running

The bsubkill utility uses the mapping policy as bsubmit. See [Configuring and running](https://github.com/IBMSpectrumComputing/lsf-utils/blob/master/bsubmit/README.md#configuring-and-running) for configuring the mapping policy for both utilities.

The bsubkill only supports killing a job by its job id with the following command:

    $ bsubkill 12345678


## Community contribution requirements

Community contributions to this repository must follow the [IBM Developer's Certificate of Origin (DCO)](https://github.com/IBMSpectrumComputing/lsf-utils/blob/master/IBMDCO.md) process and only through GitHub pull requests:

1. Contributor proposes new code to the community.

2. Contributor signs off on contributions (that is, attaches the DCO to ensure the contributor is either the code originator or has rights to publish. The template of the DCO is included in this package).
 
3. IBM Spectrum LSF Development reviews the contributions to check for the following:  
  i) Applicability and relevancy of functional content  
  ii) Any obvious issues

4. If accepted, contribution is posted. If rejected, work goes back to the contributor and is not merged.

## Copyright

&copy;Copyright IBM Corporation 2020

U.S. Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP Schedule Contract with IBM Corp.

IBM&reg;, the IBM logo, and ibm.com&reg; are trademarks of International Business Machines Corp., registered in many jurisdictions worldwide. Other product and service names might be trademarks of IBM or other companies. A current list of IBM trademarks is available on the Web at "Copyright and trademark information" at <http://www.ibm.com/legal/copytrade.shtml>.