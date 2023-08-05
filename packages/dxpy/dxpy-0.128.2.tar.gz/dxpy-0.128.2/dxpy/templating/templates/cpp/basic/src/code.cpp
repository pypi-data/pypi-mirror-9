/*
 * DX_APP_WIZARD_NAME DX_APP_WIZARD_VERSION
 * Generated by dx-app-wizard.
 *
 * Basic execution pattern: Your app will run on a single machine from
 * beginning to end.
 *
 * See https://wiki.dnanexus.com/Developer-Portal for documentation and
 * tutorials on how to modify this file.
 *
 * By default, this template uses the DNAnexus C++ JSON library and
 * the C++ bindings.
 */

#include <iostream>
#include <vector>
#include <stdint.h>

#include "dxjson/dxjson.h"
#include "dxcpp/dxcpp.h"

using namespace std;
using namespace dx;

int main(int argc, char *argv[]) {
  JSON input;
  dxLoadInput(input);

  // The variable *input* should now contain the input fields given to
  // the app(let), with keys equal to the input field names.
  //
  // For example, if an input field is of name "num" and class "int",
  // you can obtain the value via:
  //
  // int num = input["num"].get<int>();
  //
  // See https://wiki.dnanexus.com/dxjson for more details on how to
  // use the C++ JSON library.
DX_APP_WIZARD_INITIALIZE_INPUTDX_APP_WIZARD_DOWNLOAD_ANY_FILES
  // Fill in your application code here.
  //
  // To report any recognized errors, you can use the dxReportError
  // function in the dxcpp library as follows, which will also exit
  // your application with exit code 1.
  //
  //   try {
  //     <some code here>
  //   } catch (...) {
  //     dxReportError("My error message");
  //   }
DX_APP_WIZARD_UPLOAD_ANY_FILES
  // The following line(s) fill in some basic dummy output and assumes
  // that you have created variables to represent your output with the
  // same name as your output fields.

  JSON output = JSON(JSON_HASH);
DX_APP_WIZARD_OUTPUT
  dxWriteOutput(output);

  return 0;
}
