All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer. Redistributions in binary 
form must reproduce the above copyright notice, this list of conditions and the 
following disclaimer in the documentation and/or other materials provided 
with the distribution.
Neither the name of PSI nor the names of its contributors may be used 
to endorse or promote products derived from this software without specific 
prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Description: Brightway2 parameters
        =====================
        
        Library for storing, validating, and calculating with parameters. Designed to work with the `Brightway2 life cycle assessment framework <http://brightway2.readthedocs.org/en/latest/>`__, but should work for other use cases.
        
        Compatible with Python 2 & 3, tested on 2.7, 3.3, and 3.4. 100% test coverage. `Source code on bitbucket <https://bitbucket.org/cmutel/brightway2-parameters>`__, documentation on `Read the Docs <http://brightway2-parameters.readthedocs.org/>`__.
        
        Todo:
        
            * Show where there are circular references
            * MC needs an efficient way to insert values into various RNG output arrays
                * Do we need a new unique ID per exchange? Exchange input/output not guaranteed unique
                * Or somehow do something tricky during processing step?
                * Rewrite main MonteCarlo class to have view into PV lca?
        
Platform: UNKNOWN
Classifier: Development Status :: 5 - Production/Stable
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: BSD License
Classifier: Operating System :: MacOS :: MacOS X
Classifier: Operating System :: Microsoft :: Windows
Classifier: Operating System :: POSIX
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: 3.4
