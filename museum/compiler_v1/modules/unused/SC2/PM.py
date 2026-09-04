def PM_flags():
  from android.content.pm.PackageManager import PM
  names = set("GET_ACTIVITIES", "GET_CONFIGURATIONS", "GET_GIDS", "GET_INSTRUMENTATION", "GET_INTENT_FILTERS", "GET_META_DATA", "GET_PERMISSIONS", "GET_PROVIDERS", "GET_RECEIVERS", "GET_SERVICES", "GET_SHARED_LIBRARY_FILES", "GET_SIGNATURES", "GET_SIGNING_CERTIFICATES", "GET_URI_PERMISSION_PATTERNS", "MATCH_UNINSTALLED_PACKAGES", "MATCH_DISABLED_COMPONENTS", "MATCH_DISABLED_UNTIL_USED_COMPONENTS", "MATCH_SYSTEM_ONLY", "MATCH_FACTORY_ONLY", "MATCH_ANY_USER", "MATCH_DEBUG_TRIAGED_MISSING", "MATCH_INSTANT", "MATCH_APEX", "MATCH_ARCHIVED_PACKAGES", "GET_DISABLED_COMPONENTS", "GET_DISABLED_UNTIL_USED_COMPONENTS", "GET_UNINSTALLED_PACKAGES", "MATCH_HIDDEN_UNTIL_INSTALLED_COMPONENTS", "MATCH_DIRECT_BOOT_AWARE", "MATCH_DIRECT_BOOT_UNAWARE", "GET_ATTRIBUTIONS_LONG")
  items = sorted(((name, value) for name, value in PM.fields().items() if name in names), key = lambda kv: kv[1])
  print("~" * 77)
  for name, value in items: print(name, value)
  print("~" * 77)
# PM_flags()



from android.content.pm.ComponentInfo import jComponentInfo
from android.content.pm.PackageItemInfo import jPackageItemInfo
from android.os.PatternMatcher import jPatternMatcher

# https://github.com/AndroidSDKSources/android-sdk-sources-for-api-level-34/blob/master/android/content/pm/PackageItemInfo.java#L51

PackageItemInfo = (
  ("name",              "str", None),
  ("packageName",       "str", None),
  ("labelRes",          "int", 0),
  ("nonLocalizedLabel", "CharSequence", None),
  ("icon",              "int", 0),
  ("logo",              "int", 0),
  ("metaData",          "Bundle", None),
  ("banner",            "int", 0),
  ("showUserIcon",      "int", 0),
)
PackageItemInfoNode = PackageItemInfo,

# https://github.com/AndroidSDKSources/android-sdk-sources-for-api-level-34/blob/master/android/content/pm/ComponentInfo.java

ComponentInfo = (
  ("applicationInfo", "ApplicationInfo(Repeat)", None),
  ("processName",     "str",  None),
  ("splitName",       "str",  None),
  ("attributionTags", "[str", None),
  ("descriptionRes",  "int",  0),
  ("enabled",         "bool", True),
  ("exported",        "bool", False),
  ("directBootAware", "bool", False),
)
ComponentInfoNode = ComponentInfo, jPackageItemInfo, PackageItemInfoNode

# http://www.java2s.com/example/java-src/pkg/android/content/pm/applicationinfo-2595b.html

ApplicationInfo = (
  ("taskAffinity",                 "str", None),
  ("permission",                   "str", None),
  ("processName",                  "str", None),
  ("className",                    "str", None),
  ("theme",                        "int", 0),
  ("flags",                        "int", 0), # без FLAG_*
  ("privateFlags",                 "int", 0), # без PRIVATE_FLAG_*
  ("requiresSmallestWidthDp",      "int", 0),
  ("compatibleWidthLimitDp",       "int", 0),
  ("largestWidthLimitDp",          "int", 0),
  ("maxAspectRatio",               "float", 0.0),
  ("storageUuid",                  "uuid", None),
  ("volumeUuid",                   "str", None), # @Deprecated
  ("scanSourceDir",                "str", None),
  ("scanPublicSourceDir",          "str", None),
  ("sourceDir",                    "str", None),
  ("publicSourceDir",              "str", None),
  ("splitNames",                  "[str", None),
  ("splitSourceDirs",             "[str", None),
  ("splitPublicSourceDirs",       "[str", None),
  ("splitDependencies",            "sparse", None),
  ("nativeLibraryDir",             "str", None),
  ("secondaryNativeLibraryDir",    "str", None),
  ("nativeLibraryRootDir",         "str", None),
  ("nativeLibraryRootRequiresIsa", "bool", False),
  ("primaryCpuAbi",                "str", None),
  ("secondaryCpuAbi",              "str", None),
  ("resourceDirs",                "[str", None),
  ("seInfo",                       "str", None),
  ("seInfoUser",                   "str", None),
  ("sharedLibraryFiles",          "[str", None),
  ("sharedLibraryInfos",          "[SharedLibraryInfo", None),
  ("dataDir",                      "str", None),
  ("deviceProtectedDataDir",       "str", None),
  ("credentialProtectedDataDir",   "str", None),
  ("uid",                          "int", 0),
  ("minSdkVersion",                "int", 0),
  ("targetSdkVersion",             "int", 0),
  ("longVersionCode",              "long", 0),
  ("versionCode",                  "int", 0), # @Deprecated
  ("enabled",                      "bool", True),
  ("enabledSetting",               "int", 0), # PackageManager.COMPONENT_ENABLED_STATE_DEFAULT
  ("installLocation",              "int", -1), # PackageInfo.INSTALL_LOCATION_UNSPECIFIED
  ("manageSpaceActivityName",      "str", None),
  ("backupAgentName",              "str", None),
  ("descriptionRes",               "int", 0),
  ("uiOptions",                    "int", 0),
  ("fullBackupContent",            "int", 0),
  ("networkSecurityConfigRes",     "int", 0),
  ("category",                     "int", -1), # CATEGORY_UNDEFINED
  ("targetSandboxVersion",         "int", 0),
  ("classLoaderName",              "str", None),
  ("splitClassLoaderNames",       "[str", None),
  ("compileSdkVersion",            "int", 0),
  ("compileSdkVersionCodename",    "str", None),
  ("appComponentFactory",          "str", None),
  ("mHiddenApiPolicy",             "int", -1), # HIDDEN_API_ENFORCEMENT_DEFAULT
  ("hiddenUntilInstalled",         "bool", False),
)
ApplicationInfoNode = ApplicationInfo, jPackageItemInfo, PackageItemInfoNode

# https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/content/pm/SharedLibraryInfo.java

SharedLibraryInfo = (
  ("mPath",                      "str",       None),
  ("mPackageName",               "str",       None),
  ("mCodePaths",                 "List<str>", None),
  ("mName",                      "str",       None),
  ("mVersion",                   "long",      0),
  ("mType",                      "int",       0),
  ("mDeclaringPackage",          "VersionedPackage",        None),
  ("mDependentPackages",         "List<VersionedPackage>",  None),
  ("mDependencies",              "List<SharedLibraryInfo>", None),
  ("mIsNative",                  "bool",                    False),
  ("mOptionalDependentPackages", "List<VersionedPackage>",  None),
)
SharedLibraryInfoNode = ApplicationInfo, jPackageItemInfo, PackageItemInfoNode

# ...

# max API 35, 36?
# http://www.java2s.com/example/java-src/pkg/android/content/pm/activityinfo-22753.html

WindowLayout = ( # ActivityInfo$WindowLayout
  ("width",          "int",   0),
  ("widthFraction",  "float", 0.),
  ("height",         "int",   0),
  ("heightFraction", "float", 0.),
  ("gravity",        "int",   0),
  ("minWidth",       "int",   0),
  ("minHeight",      "int",   0),
)
ActivityInfo = (
  ("theme",                "int", 0),
  ("launchMode",           "int", 0), # LAUNCH_MULTIPLE
  ("documentLaunchMode",   "int", 0), # DOCUMENT_LAUNCH_NONE
  ("permission",           "str", None),
  ("taskAffinity",         "str", None),
  ("targetActivity",       "str", None),
  ("launchToken",          "str", None),
  ("flags",                "int", 0), # без FLAG_*
  ("screenOrientation",    "int", -1), # SCREEN_ORIENTATION_UNSPECIFIED
  ("configChanges",        "int", 0), # без CONFIG_*
  ("softInputMode",        "int", 0),
  ("uiOptions",            "int", 0), # без UIOPTION_SPLIT_ACTION_BAR_WHEN_NARROW = 1
  ("parentActivityName",   "str", None),
  ("persistableMode",      "int", 0), # PERSIST_ROOT_ONLY
  ("maxRecents",           "int", 0),
  ("lockTaskLaunchMode",   "int", 0), # LOCK_TASK_LAUNCH_MODE_DEFAULT
  ("windowLayout",         "WindowLayout", None),
  ("resizeMode",           "int", 2), # RESIZE_MODE_RESIZEABLE
  ("requestedVrComponent", "str", None),
  ("rotationAnimation",    "int", -1),
  ("colorMode",            "int", 0), # COLOR_MODE_DEFAULT
  ("maxAspectRatio",       "float", 0.),
)
WindowLayoutNode = WindowLayout,
ActivityInfoNode = ActivityInfo, jComponentInfo, ComponentInfoNode

# http://www.java2s.com/example/java-src/pkg/android/content/pm/serviceinfo-2f3b9.html

ServiceInfo = (
  ("permission", "str", None),
  ("flags",      "int", 0),
)
ServiceInfoNode = ServiceInfo, jComponentInfo, ComponentInfoNode

# http://www.java2s.com/example/java-src/pkg/android/os/patternmatcher-aed1f.html

PatternMatcher = (
  ("mPattern",        "str", None),
  ("mType",           "int", 0),
  ("mParsedPattern", "[int", None),
)
PatternMatcherNode = PatternMatcher,

# http://www.java2s.com/example/java-src/pkg/android/content/pm/pathpermission-ab1b0.html

PathPermission = (
  ("mReadPermission",  "str", None),
  ("mWritePermission", "str", None),
)
PathPermissionNode = PathPermission, jPatternMatcher, PatternMatcherNode

# http://www.java2s.com/example/java-src/pkg/android/content/pm/providerinfo-b148a.html

ProviderInfo = (
  ("authority",              "str", None),
  ("readPermission",         "str", None),
  ("writePermission",        "str", None),
  ("grantUriPermissions",    "bool", False),
  ("uriPermissionPatterns", "[PatternMatcher", None),
  ("pathPermissions",       "[PathPermission", None),
  ("multiprocess",           "bool", False),
  ("initOrder",              "int", None),
  ("flags",                  "int", 0), # без FLAG_*
  ("isSyncable",             "bool", False), # @Deprecated
)
ProviderInfoNode = ProviderInfo, jComponentInfo, ComponentInfoNode

# http://www.java2s.com/example/java-src/pkg/android/content/pm/instrumentationinfo-7fd90.html

InstrumentationInfo = (
  ("targetPackage",              "str", None),
  ("targetProcesses",            "str", None),
  ("sourceDir",                  "str", None),
  ("publicSourceDir",            "str", None),
  ("splitNames",                "[str", None),
  ("splitSourceDirs",           "[str", None),
  ("splitPublicSourceDirs",     "[str", None),
  ("splitDependencies",          "sparse", None),
  ("dataDir",                    "str", None),
  ("deviceProtectedDataDir",     "str", None),
  ("credentialProtectedDataDir", "str", None),
  ("primaryCpuAbi",              "str", None),
  ("secondaryCpuAbi",            "str", None),
  ("nativeLibraryDir",           "str", None),
  ("secondaryNativeLibraryDir",  "str", None),
  ("handleProfiling",            "bool", False),
  ("functionalTest",             "bool", False),
)
InstrumentationInfoNode = InstrumentationInfo, jPackageItemInfo, PackageItemInfoNode

# http://www.java2s.com/example/java-src/pkg/android/content/pm/permissioninfo-68640.html

PermissionInfo = (
  ("protectionLevel",         "int", 0), # PROTECTION_NORMAL и без PROTECTION_FLAG_*   @Deprecated
  ("flags",                   "int", 0), # без FLAG_*
  ("group",                   "str", None),
  ("descriptionRes",          "int", 0),
  ("requestRes",              "int", 0),
  ("nonLocalizedDescription", "CharSequence", None),
)
PermissionInfoNode = PermissionInfo, jPackageItemInfo, PackageItemInfoNode

# http://www.java2s.com/example/java-src/pkg/android/content/pm/signature-ad39a.html

Signature = (
  ("mSignature",         "bytes", None),
  ("mCertificateChain", "[Certificate", None),
)
SignatureNode = Signature,

# https://android.googlesource.com/platform/prebuilts/fullsdk/sources/+/dc3f885ebe8ddc75bd9cf2d567eef4d1ed433a09/android-35/android/content/pm/SigningInfo.java
# https://android.googlesource.com/platform/prebuilts/fullsdk/sources/+/dc3f885ebe8ddc75bd9cf2d567eef4d1ed433a09/android-35/android/content/pm/SigningDetails.java

SigningInfo = (
  ("mSignatures",              "[Signature", None),
  ("mSignatureSchemeVersion",   "int",       0), # SignatureSchemeVersion.UNKNOWN
  ("mPublicKeys",               "ArraySet",  None),
  ("mPastSigningCertificates", "[Signature", None),
)
SigningInfoNode = SigningInfo,

# http://www.java2s.com/example/java-src/pkg/android/content/pm/configurationinfo-2d997.html

ConfigurationInfo = (
  ("reqTouchScreen",   "int", 0), # android.content.res.Configuration.TOUCHSCREEN_UNDEFINED
  ("reqKeyboardType",  "int", 0), # android.content.res.Configuration.KEYBOARD_UNDEFINED
  ("reqNavigation",    "int", 0), # android.content.res.Configuration.NAVIGATION_UNDEFINED
  ("reqInputFeatures", "int", 0), # без INPUT_FEATURE_*
  ("reqGlEsVersion",   "int", 0), # GL_ES_VERSION_UNDEFINED
)
ConfigurationInfoNode = ConfigurationInfo,

# http://www.java2s.com/example/java-src/pkg/android/content/pm/featureinfo-41ef1.html

FeatureInfo = (
  ("name",           "str", None),
  ("version",        "int", 0),
  ("reqGlEsVersion", "int", 0), # GL_ES_VERSION_UNDEFINED
  ("flags",          "int", 0), # без FLAG_REQUIRED = 1
)
FeatureInfoNode = FeatureInfo,

FeatureGroupInfo = (
  ("features", "[FeatureInfo", None),
)
FeatureGroupInfoNode = FeatureGroupInfo,



PackageInfo = (
  ("packageName",                "str", None),
  ("splitNames",                "[str", None),
  ("versionCode",                "int", 0), # @Deprecated
  ("versionCodeMajor",           "int", 0),
  ("versionName",                "str", None),
  ("baseRevisionCode",           "int", 0),
  ("splitRevisionCodes",        "[int", None),
  ("sharedUserId",               "str", None),
  ("sharedUserLabel",            "int", 0),
  ("applicationInfo",            "ApplicationInfo", None),
  ("firstInstallTime",           "long", 0),
  ("lastUpdateTime",             "long", 0),
  ("gids",                      "[int", None),
  ("activities",                "[ActivityInfo", None),
  ("receivers",                 "[ActivityInfo", None),
  ("services",                  "[ServiceInfo",  None),
  ("providers",                 "[ProviderInfo", None),
  ("instrumentation",           "[InstrumentationInfo", None),
  ("permissions",               "[PermissionInfo", None),
  ("requestedPermissions",      "[str", None),
  ("requestedPermissionsFlags", "[int", None), # каждый элемент массива: без REQUESTED_PERMISSION_*
  ("signatures",                "[Signature", None), # @Deprecated
  ("configPreferences",         "[ConfigurationInfo", None),
  ("reqFeatures",               "[FeatureInfo", None),
  ("featureGroups",             "[FeatureGroupInfo", None),
  ("installLocation",           "int", 1), # INSTALL_LOCATION_INTERNAL_ONLY
  ("isStub",                    "bool", False),
  ("coreApp",                   "bool", False),
  ("requiredForAllUsers",       "bool", False),
  ("restrictedAccountType",     "str", None),
  ("requiredAccountType",       "str", None),
  ("overlayTarget",             "str", None),
  ("overlayCategory",           "str", None),
  ("overlayPriority",           "int", 0),
  ("mOverlayIsStatic",          "bool", False),
  ("compileSdkVersion",         "int", 0),
  ("compileSdkVersionCodename", "str", None),
  ("signingInfo",               "SigningInfo", None),
  ("isApex",                    "bool", False),
  # запихивает во все activities, receivers, services и providers
  # один и тот же applicationInfo, определённый здесь (если не определён, ничего не делает)
)
PackageInfoNode = PackageInfo,



PM_types = {
  "ApplicationInfo":     ApplicationInfoNode,
  "PatternMatcher":      PatternMatcherNode,
  "PathPermission":      PathPermissionNode,
  "SharedLibraryInfo":   SharedLibraryInfoNode,
	 # ...
  "WindowLayout":        WindowLayoutNode,
  "ActivityInfo":        ActivityInfoNode,
  "ServiceInfo":         ServiceInfoNode,
  "ProviderInfo":        ProviderInfoNode,
  "InstrumentationInfo": InstrumentationInfoNode,
  "PermissionInfo":      PermissionInfoNode,
  "Signature":           SignatureNode,
  "SigningInfo":         SigningInfoNode,
  "ConfigurationInfo":   ConfigurationInfoNode,
  "FeatureInfo":         FeatureInfoNode,
  "FeatureGroupInfo":    FeatureGroupInfoNode,
  # ...
  "PackageInfo":         PackageInfoNode,
}



class PM_item:
  cache = {}
  def __init__(self, obj, type_name):
    self.obj = obj
    self.type_name = type_name
    self.type = PM_types[type_name]
    key = obj, type_name
    cache = PM_item.cache.get(key, None)
    if cache is None:
      self.fields = {}
      self.types = []
      self.field_reader(self.type, obj)
      self.parse()
      PM_item.cache[key] = self.fields, self.types, self.list, self.dict
    else:
      self.fields, self.types, self.list, self.dict = cache
      print("CACHE! ;'-}")
  def field_reader(self, type, node):
    if len(type) == 3:
      type, jType, nextType = type
      nextNode = node.cast(jType)
      self.field_reader(nextType, nextNode)
    else: type = type[0]
    self.fields.update(node.fields())
    self.types.extend(type)
  def parse(self):
    fields = self.fields
    list, dict = [], {}
    for name, T, default in self.types:
      value = fields.get(name, default)
      if value is not None:
        is_arr = T[0] == "["
        if is_arr: T = T[1:]
        type = PM_types.get(T, None)
        if type is not None:
          if is_arr:
            value = [PM_item(item, T) for item in value]
          else: value = PM_item(value, T)
        elif is_arr: value = value[:]
      list.append(value)
      dict[name] = value
    self.list = list
    self.dict = dict
  def __str__(self, level = 0):
    arr = []
    dict = self.dict
    if self.type_name in ("ActivityInfo", "ServiceInfo", "ProviderInfo", "InstrumentationInfo", "PermissionInfo"): level = -1
    if level >= 0:
      prefix = "\n" + "  " * level
      level += 1
      prefix2 = "\n" + "  " * level
      level2 = level + 1
      prefix3 = "\n" + "  " * level2
    else:
      prefix = prefix2 = prefix3 = " "
    for name, T, default in self.types:
      value = dict[name]
      is_arr = T[0] == "["
      if is_arr: T = T[1:]
      primitive = T not in PM_types
      if value is None:
        value = repr(value)
      elif is_arr:
        if not value: value = "[]"
        elif primitive: value = repr(value)
        else: value = "[%s%s%s]" % (prefix3, ("," + prefix3).join(item.__str__(level2) for item in value), prefix2)
      elif primitive:
        if T == "uuid": value = "UUID:" + value._m_toString()
        else: value = repr(value)
      else:
        value = value.__str__(level)
      arr.append("%s: %s" % (name, value))
    return "%s:{%s%s%s}" % (self.type_name, prefix2, ("," + prefix2).join(arr), prefix)



def PM_getter(flags = 0):
  from pbi.sc2.Meaterson import Meaterson
  from android.content.Context import Context
  from android.content.pm.Signature import Signature

  # activity = Meaterson._f_boss
  context = Meaterson._f_context.cast(Context)
  PM = context._m_getPackageManager()
  # PN = context._m_getPackageName()
  PN = "com.scrap.clicker.android"

  """
GET_ACTIVITIES 1
GET_RECEIVERS 2
GET_SERVICES 4
GET_PROVIDERS 8
GET_INSTRUMENTATION 16
GET_INTENT_FILTERS 32
GET_SIGNATURES 64
GET_META_DATA 128
GET_GIDS 256
GET_DISABLED_COMPONENTS 512
GET_SHARED_LIBRARY_FILES 1024
GET_URI_PERMISSION_PATTERNS 2048
GET_PERMISSIONS 4096
GET_UNINSTALLED_PACKAGES 8192
GET_CONFIGURATIONS 16384
GET_DISABLED_UNTIL_USED_COMPONENTS 32768
GET_SIGNING_CERTIFICATES 134217728
"""

  return PM._m_getPackageInfo(PN, flags)

def PM_extractor():
  item = PM_getter(0x800ffff)
  print("applicationInfo:", repr(item))
  obj = PM_item(item, "PackageInfo")
  print("• obj:", obj.__str__())

  """
  print("PM:", PM, PN, info)

  orig = Signature(Signaturer._m_a())
  for sign in (item._f_signatures[0], orig):
    data = sign._m_toByteArray()
    # sign._m_toCharsString() == data.hex() -> True
    print("sign:", len(data), data.hex(), sign._m_hashCode())
  """
