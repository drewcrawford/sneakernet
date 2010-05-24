GWTPATH=/Applications/eclipse/plugins/com.google.gwt.eclipse.sdkbundle.2.0.0_2.0.0.v200912062003/gwt-2.0.0/
rm -rf appengine/static
java -Xmx512M -classpath ${GWTPATH}gwt-dev.jar:${GWTPATH}gwt-user.jar:supergwt/src com.google.gwt.dev.Compiler -war appengine/static com.awesome.gwt.Supergwt
cp supergwt/war/Supergwt.* appengine/static/
echo "compling mac..."
rm sneak.pyo
python -OO pyongyang.py
cd macport
xcodebuild clean
rm -rf macport/build/Release/*
xcodebuild -activetarget -activeconfiguration
chmod -R +x macport/build/Release/*
cd ..
rm appengine/sneakernet-mac.dmg
rm macport/build/Release/*.dSYM
hdiutil create -srcfolder "macport/build/Release/" -noanyowners -volname "Sneakernet" sneakernet-mac.dmg
mv sneakernet-mac.dmg appengine/
hdiutil internet-enable -yes sneakernet-mac.dmg
echo "compiling win..."
rm appengine/sneakernet-win.zip
zip appengine/sneakernet-win.zip sneak.pyo bcrypt.exe zlib.dll run-sneakernet.bat