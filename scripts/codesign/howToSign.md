
You must first create the OS X app by running the `packagme.sh` script with the **_deployment_** option

`./scripts/packageme deploy`

Run the following scripts from the project root;  Save the submission ID 
from step 3

1. `./scripts/codesign/python39zipsign.sh`
2. `./scripts/codesign/signapp.sh`
3. `./scripts/codesign/notarizeapp.sh`
4. `./scripts/codesign/stapleapp.sh `
5. `./scripts/codesign/verifysigning.sh`


Once the above completes remove the zip created by `notarizeapp.sh` and rezip the application.
That is the file I put on the GitHub release as a binary.



https://developer.apple.com/forums/thread/130855
