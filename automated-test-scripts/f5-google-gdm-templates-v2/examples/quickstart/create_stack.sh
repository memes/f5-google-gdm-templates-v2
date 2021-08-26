#  expectValue = "completed successfully"
#  scriptTimeout = 5
#  replayEnabled = false
#  replayTimeout = 0

tmpl_path="/tmp/examples/quickstart/"

# grab template and schema
cp -r $PWD/examples /tmp

# Run GDM quickstart template
cp /tmp/examples/quickstart/sample_quickstart.yaml ${tmpl_path}<DEWPOINT JOB ID>.yaml
# Update Config File using sample_quickstart.yaml 
/usr/bin/yq e ".resources[0].name = \"quickstart-py\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressApp = \"<RESTRICTED SRC ADDRESS APP>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressAppInternal = \"<RESTRICTED SRC ADDRESS APP INTERNAL>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.restrictedSrcAddressMgmt = \"<RESTRICTED SRC ADDRESS>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitConfig = \"<BIGIP RUNTIME INIT CONFIG>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.bigIpRuntimeInitPackageUrl = \"<BIGIP RUNTIME INIT PACKAGEURL>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.imageName = \"<IMAGE NAME>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.instanceType = \"<INSTANCE TYPE>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.numNics = <NUMBER NICS>" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.region = \"<REGION>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.uniqueString = \"<UNIQUESTRING>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].properties.zone = \"<AVAILABILITY ZONE>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml
/usr/bin/yq e ".resources[0].type = \"<TEMPLATE NAME>\"" -i ${tmpl_path}<DEWPOINT JOB ID>.yaml

# print out config file
/usr/bin/yq e ${tmpl_path}<DEWPOINT JOB ID>.yaml
labels="delete=true"
gcloud="gcloud deployment-manager deployments create <STACK NAME> --labels $labels --config ${tmpl_path}<DEWPOINT JOB ID>.yaml"
$gcloud
