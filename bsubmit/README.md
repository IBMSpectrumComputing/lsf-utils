# bsubmit

bsubmit is a wrapper of bsub. It allows users to submit jobs as another user.

If you would like to contribute, you must follow the DCO process in the attached [DCO Readme file](https://github.com/IBMSpectrumComputing/lsf-utils/blob/master/IBMDCO.md) in the root of this repository.  It essentially requires you to provide a Sign Off line in the notes of your pull request stating that the work does not infinge on the work of others.  For more details, refer to the DCO Readme file.

## Release Information

* IBM Spectrum LSF bsubmit
* Supporting LSF Release: 10.1
* Wrapper Version: 1.0
* Publication date: 2 Jul 2020
* Last modified: 2 Jul 2020

## Contents

* Introduction
* Supported platforms
* Building and installing
* Configuring and running
* Release notes
* Community contribution requirements
* Copyright
 
## Introduction

You might want to make the job submission user be a particular user, but map the job execution user to various users. 

To do this, this package introduces a bsub wrapper with the setuid bit set. The wrapper accepts the --user option and verifies if the mapping is valid using a configuration file. 

## Supported platforms

This package is only tested on Linux platforms.

Supported operating systems:  
Linux 2.6, glibc 2.3, x86-64: RHEL 6.2, 6.4, 6.5, 6.8  
Linux 3.10, glibc 2.17, x86-64: RHEL 7.4, 7.5

## Building and installing

Before building, set the LSF environment variables:

    $ source profile.lsf

To build and install, go to the main source directory and run the following commands:

    $ make
    $ make install

A new executable file named bsubmit is installed in the $LSF_BINDIR directory. Ensure that the file is owned by root and has the setuid bit enabled. To do this, you must have root privileges.

## Configuring and running

Create a configuration file to define the user mapping policy named lsf.usermapping in the $LSF_ENVDIR/ directory.

For example:

    $ cat $LSF_ENVDIR/lsf.usermapping
    #submit users or groups   #execute users or groups
    cromwell                  bpappas,cking,apappas
    pmgroup                   jgroup

This means that user cromwell can submit jobs as user bpappas, cking, or apappas. Users in pmgroup can submit jobs as users in jgroup.

This file must be owned by the LSF administrator, and have read/write access for the file owner with read-only access to the group and other users for security considerations.

To submit jobs as another user, run the following command:

    $ bsubmit --user apappas sleep 10

## Release notes

### Release 1.0

- This is the first release.
- Tested with LSF 10.1 on Linux 2.6 and 3.10.

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
