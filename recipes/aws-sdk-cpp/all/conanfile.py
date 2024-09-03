import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class AwsSdkCppConan(ConanFile):
    name = "aws-sdk-cpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/aws-sdk-cpp"
    description = "AWS SDK for C++"
    topics = ("aws", "cpp", "cross-platform", "amazon", "cloud")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    # This list comes from tools/code-generation/api-description, which then generate the sdk sources
    # To generate the list, run the following snippet in said folder:
    # sorted(list(set(n if "." not in n else "".join(n.split(".")[1:]) + "-" + n.split(".")[0] for n in [f.rsplit("-", 3)[0] for f in os.listdir(".")])))
    # The .split("-") is to remove the version number (api date) from the file name
    # The .split(".") shenanigans is to match the generated name with the one described in sdksCommon.cmake
    _sdks = (
        "access-management",
        "accessanalyzer",
        "acm",
        "acm-pca",
        "alexaforbusiness",
        "amp",
        "amplify",
        "amplifybackend",
        "apigateway",
        "apigatewaymanagementapi",
        "apigatewayv2",
        "appconfig",
        "appflow",
        "appintegrations",
        "application-autoscaling",
        "application-insights",
        "appmesh",
        "appstream",
        "appsync",
        "athena",
        "auditmanager",
        "autoscaling",
        "autoscaling-plans",
        "awstransfer",
        "backup",
        "batch",
        "braket",
        "budgets",
        "ce",
        "chime",
        "cloud9",
        "clouddirectory",
        "cloudformation",
        "cloudfront",
        "cloudhsm",
        "cloudhsmv2",
        "cloudsearch",
        "cloudsearchdomain",
        "cloudtrail",
        "codeartifact",
        "codebuild",
        "codecommit",
        "codedeploy",
        "codeguru-reviewer",
        "codeguruprofiler",
        "codepipeline",
        "codestar",
        "codestar-connections",
        "codestar-notifications",
        "cognito-identity",
        "cognito-idp",
        "cognito-sync",
        "comprehend",
        "comprehendmedical",
        "compute-optimizer",
        "config",
        "connect",
        "connect-contact-lens",
        "connectparticipant",
        "cur",
        "customer-profiles",
        "databrew",
        "dataexchange",
        "datapipeline",
        "datasync",
        "dax",
        "detective",
        "devicefarm",
        "devops-guru",
        "directconnect",
        "discovery",
        "dlm",
        "dms",
        "docdb",
        "ds",
        "dynamodb",
        "dynamodbstreams",
        "ebs",
        "ec2",
        "ec2-instance-connect",
        "ecr",
        "ecr-public",
        "ecs",
        "eks",
        "elastic-inference",
        "elasticache",
        "elasticbeanstalk",
        "elasticfilesystem",
        "elasticloadbalancing",
        "elasticloadbalancingv2",
        "elasticmapreduce",
        "elastictranscoder",
        "email",
        "emr-containers",
        "es",
        "eventbridge",
        "events",
        "firehose",
        "fms",
        "forecast",
        "forecastquery",
        "frauddetector",
        "fsx",
        "gamelift",
        "glacier",
        "globalaccelerator",
        "glue",
        "greengrass",
        "greengrassv2",
        "groundstation",
        "guardduty",
        "health",
        "healthlake",
        "honeycode",
        "iam",
        "identity-management",
        "identitystore",
        "imagebuilder",
        "importexport",
        "inspector",
        "iot",
        "iot-data",
        "iot-jobs-data",
        "iot1click-devices",
        "iot1click-projects",
        "iotanalytics",
        "iotdeviceadvisor",
        "iotevents",
        "iotevents-data",
        "iotfleethub",
        "iotsecuretunneling",
        "iotsitewise",
        "iotthingsgraph",
        "iotwireless",
        "ivs",
        "kafka",
        "kendra",
        "kinesis",
        "kinesis-video-archived-media",
        "kinesis-video-media",
        "kinesis-video-signaling",
        "kinesisanalytics",
        "kinesisanalyticsv2",
        "kinesisvideo",
        "kms",
        "lakeformation",
        "lambda",
        "lex",
        "lex-models",
        "lexv2-models",
        "lexv2-runtime",
        "license-manager",
        "lightsail",
        "location",
        "logs",
        "lookoutvision",
        "machinelearning",
        "macie",
        "macie2",
        "managedblockchain",
        "marketplace-catalog",
        "marketplace-entitlement",
        "marketplacecommerceanalytics",
        "mediaconnect",
        "mediaconvert",
        "medialive",
        "mediapackage",
        "mediapackage-vod",
        "mediastore",
        "mediastore-data",
        "mediatailor",
        "meteringmarketplace",
        "migrationhub-config",
        "mobile",
        "mobileanalytics",
        "monitoring",
        "mq",
        "mturk-requester",
        "mwaa",
        "neptune",
        "network-firewall",
        "networkmanager",
        "opsworks",
        "opsworkscm",
        "organizations",
        "outposts",
        "personalize",
        "personalize-events",
        "personalize-runtime",
        "pi",
        "pinpoint",
        "pinpoint-email",
        "polly",
        "polly-sample",
        "pricing",
        "qldb",
        "qldb-session",
        "queues",
        "quicksight",
        "ram",
        "rds",
        "rds-data",
        "redshift",
        "redshift-data",
        "rekognition",
        "resource-groups",
        "resourcegroupstaggingapi",
        "robomaker",
        "route53",
        "route53domains",
        "route53resolver",
        "s3",
        "s3-crt",
        "s3-encryption",
        "s3control",
        "s3outposts",
        "sagemaker",
        "sagemaker-a2i-runtime",
        "sagemaker-edge",
        "sagemaker-featurestore-runtime",
        "sagemaker-runtime",
        "savingsplans",
        "schemas",
        "sdb",
        "secretsmanager",
        "securityhub",
        "serverlessrepo",
        "service-quotas",
        "servicecatalog",
        "servicecatalog-appregistry",
        "servicediscovery",
        "sesv2",
        "shield",
        "signer",
        "sms",
        "sms-voice",
        "snowball",
        "sns",
        "sqs",
        "ssm",
        "sso",
        "sso-admin",
        "sso-oidc",
        "states",
        "storagegateway",
        "sts",
        "support",
        "swf",
        "synthetics",
        "text-to-speech",
        "textract",
        "timestream-query",
        "timestream-write",
        "transcribe",
        "transcribestreaming",
        "transfer",
        "translate",
        "waf",
        "waf-regional",
        "wafv2",
        "wellarchitected",
        "workdocs",
        "worklink",
        "workmail",
        "workmailmessageflow",
        "workspaces",
        "xray",
    )
    options = {
        **{
            "shared": [True, False],
            "fPIC": [True, False],
            "min_size": [True, False],
        },
        **{ x: [True, False] for x in _sdks},
    }
    default_options = {key: False for key in options.keys()}
    default_options["fPIC"] = True
    default_options["identity-management"] = True
    default_options["access-management"] = True
    default_options["queues"] = True
    default_options["transfer"] = True
    default_options["s3-encryption"] = True
    default_options["text-to-speech"] = True
    default_options["monitoring"] = True

    short_paths = True

    @property
    def _internal_requirements(self):
        return {
            "access-management": ["iam", "cognito-identity"],
            "identity-management": ["cognito-identity", "sts"],
            "queues": ["sqs"],
            "s3-encryption": ["s3", "kms"],
            "text-to-speech": ["polly"],
            "transfer": ["s3"],
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.version == "1.11.352":
            self.requires("aws-crt-cpp/0.26.9", transitive_headers=True)
            self.requires("aws-c-auth/0.7.16")
            self.requires("aws-c-cal/0.6.14")
            self.requires("aws-c-common/0.9.15")
            # self.requires("aws-c-compression/0.2.18")
            self.requires("aws-c-event-stream/0.4.2")
            self.requires("aws-c-http/0.8.1")
            self.requires("aws-c-io/0.14.7")
            self.requires("aws-c-mqtt/0.10.3")
            if self.options.get_safe("s3-crt"):
                self.requires("aws-c-s3/0.5.5")
            # self.requires("aws-c-sdkutils/0.1.15")
            self.requires("aws-checksums/0.1.18")
            # missing aws-lc
            # self.requires("s2n/1.4.16")
        if self.version == "1.9.234":
            self.requires("aws-c-common/0.6.11")
            self.requires("aws-c-event-stream/0.2.7")
            self.requires("aws-checksums/0.1.12")
            self.requires("aws-c-cal/0.5.12")
            self.requires("aws-c-http/0.6.7")
            self.requires("aws-c-io/0.10.9")
            self.requires("aws-crt-cpp/0.17.1a", transitive_headers=True)
            if self.options.get_safe("s3-crt"):
                self.requires("aws-c-s3/0.1.26")
        if self.settings.os != "Windows":
            # Used transitively in core/utils/crypto/openssl/CryptoImpl.h public header
            self.requires("openssl/[>=1.1 <4]", transitive_headers=True)
            # Used transitively in core/http/curl/CurlHandleContainer.h public header
            self.requires("libcurl/[>=7.78.0 <9]", transitive_headers=True)
        if self.settings.os =="Linux":
            # Pulseaudio -> libcap, libalsa only support linux, don't use pulseaudio on other platforms
            if self.options.get_safe("text-to-speech"):
                # Used transitively in text-to-speech/PulseAudioPCMOutputDriver.h public header
                self.requires("pulseaudio/14.2", transitive_headers=True, transitive_libs=True)
        # zlib is used if ENABLE_ZLIB_REQUEST_COMPRESSION is enabled, set ot ON by default
        self.requires("zlib/[>=1.2.11 <2]")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def validate_build(self):
        if self._settings_build.os == "Windows" and self.settings.os == "Android":
            raise ConanInvalidConfiguration("Cross-building from Windows to Android is not supported")

    def validate(self):
        if (self.options.shared
            and self.settings.compiler == "gcc"
            and Version(self.settings.compiler.version) < "6.0"):
            raise ConanInvalidConfiguration(
                "Doesn't support gcc5 / shared. "
                "See https://github.com/conan-io/conan-center-index/pull/4401#issuecomment-802631744"
            )
        if is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Static runtime is not working for more recent releases")

    def package_id(self):
        for hl_comp in self._internal_requirements.keys():
            if getattr(self.info.options, hl_comp):
                for internal_requirement in self._internal_requirements[hl_comp]:
                    setattr(self.info.options, internal_requirement, True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # All option() are defined before project() in upstream CMakeLists,
        # therefore we must use cache_variables

        build_only = ["core"]
        for sdk in self._sdks:
            if self.options.get_safe(sdk):
                build_only.append(sdk)
        tc.cache_variables["BUILD_ONLY"] = ";".join(build_only)

        tc.cache_variables["ENABLE_UNITY_BUILD"] = True
        tc.cache_variables["ENABLE_TESTING"] = False
        tc.cache_variables["AUTORUN_UNIT_TESTS"] = False
        tc.cache_variables["BUILD_DEPS"] = False
        if self.settings.os != "Windows":
            tc.cache_variables["ENABLE_OPENSSL_ENCRYPTION"] = True

        tc.cache_variables["MINIMIZE_SIZE"] = self.options.min_size
        if is_msvc(self):
            tc.cache_variables["FORCE_SHARED_CRT"] = not is_msvc_static_runtime(self)

        if cross_building(self):
            tc.cache_variables["CURL_HAS_H2_EXITCODE"] = "0"
            tc.cache_variables["CURL_HAS_H2_EXITCODE__TRYRUN_OUTPUT"] = ""
            tc.cache_variables["CURL_HAS_TLS_PROXY_EXITCODE"] = "0"
            tc.cache_variables["CURL_HAS_TLS_PROXY_EXITCODE__TRYRUN_OUTPUT"] = ""
        if is_msvc(self):
            tc.preprocessor_definitions["_SILENCE_CXX17_OLD_ALLOCATOR_MEMBERS_DEPRECATION_WARNING"] = "1"
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Disable warnings as errors
        if self.version == "1.9.234":
            replace_in_file(
                self, os.path.join(self.source_folder, "cmake", "compiler_settings.cmake"),
                'list(APPEND AWS_COMPILER_WARNINGS "-Wall" "-Werror" "-pedantic" "-Wextra")', "",
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _res_folder(self):
        return "res"

    def _create_project_cmake_module(self):
        # package files needed to build other components (e.g. aws-cdi-sdk) with this SDK
        dependant_files = [
            "cmake/compiler_settings.cmake",
            "cmake/initialize_project_version.cmake",
            "cmake/utilities.cmake",
            "cmake/sdk_plugin_conf.cmake",
            "toolchains/cmakeProjectConfig.cmake",
            "toolchains/pkg-config.pc.in"
        ]
        if Version(self.version) >= "1.11.352":
            dependant_files.append("src/aws-cpp-sdk-core/include/aws/core/VersionConfig.h")
        else:
            dependant_files.append("aws-cpp-sdk-core/include/aws/core/VersionConfig.h")
        for file in dependant_files:
            copy(self, file, src=self.source_folder, dst=os.path.join(self.package_folder, self._res_folder))
            replace_in_file(
                self, os.path.join(self.package_folder, self._res_folder, file),
                "CMAKE_CURRENT_SOURCE_DIR", "AWS_NATIVE_SDK_ROOT",
                strict=False,
            )

        # avoid getting error from hook
        rename(self, os.path.join(self.package_folder, self._res_folder, "toolchains", "cmakeProjectConfig.cmake"),
                     os.path.join(self.package_folder, self._res_folder, "toolchains", "cmakeProjectConf.cmake"))
        replace_in_file(
            self, os.path.join(self.package_folder, self._res_folder, "cmake", "utilities.cmake"),
            "cmakeProjectConfig.cmake", "cmakeProjectConf.cmake",
        )

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if is_msvc(self):
            copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            rm(self, "*.lib", os.path.join(self.package_folder, "bin"))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        self._create_project_cmake_module()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "AWSSDK")

        sdk_plugin_conf = os.path.join(self._res_folder, "cmake", "sdk_plugin_conf.cmake")
        self.cpp_info.set_property("cmake_build_modules", [sdk_plugin_conf])

        # core component
        self.cpp_info.components["core"].set_property("cmake_target_name", "AWS::aws-sdk-cpp-core")
        self.cpp_info.components["core"].set_property("pkg_config_name", "aws-sdk-cpp-core")
        self.cpp_info.components["core"].libs = ["aws-cpp-sdk-core"]
        self.cpp_info.components["core"].requires = [
            "zlib::zlib",
            "aws-c-common::aws-c-common",
            "aws-c-event-stream::aws-c-event-stream",
            "aws-checksums::aws-checksums",
            "aws-c-cal::aws-c-cal",
            "aws-c-http::aws-c-http",
            "aws-c-io::aws-c-io",
            "aws-crt-cpp::aws-crt-cpp",
        ]

        if Version(self.version) >= "1.11.352":
            self.cpp_info.components["core"].requires.extend([
                "aws-c-auth::aws-c-auth",
                "aws-c-mqtt::aws-c-mqtt"
            ])

        # other components
        enabled_sdks = [sdk for sdk in self._sdks if self.options.get_safe(sdk)]
        for hl_comp in self._internal_requirements.keys():
            if getattr(self.options, hl_comp):
                for internal_requirement in self._internal_requirements[hl_comp]:
                    if internal_requirement not in enabled_sdks:
                        enabled_sdks.append(internal_requirement)

        for sdk in enabled_sdks:
            # TODO: there is no way to properly emulate COMPONENTS names for
            #       find_package(AWSSDK COMPONENTS <sdk>) in set_property()
            #       right now: see https://github.com/conan-io/conan/issues/10258
            self.cpp_info.components[sdk].set_property("cmake_target_name", f"AWS::aws-sdk-cpp-{sdk}")
            self.cpp_info.components[sdk].set_property("pkg_config_name", f"aws-sdk-cpp-{sdk}")
            self.cpp_info.components[sdk].requires = ["core"]
            if sdk in self._internal_requirements:
                self.cpp_info.components[sdk].requires.extend(self._internal_requirements[sdk])
            self.cpp_info.components[sdk].libs = ["aws-cpp-sdk-" + sdk]

            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self.cpp_info.components[sdk].names["cmake_find_package"] = "aws-sdk-cpp-" + sdk
            self.cpp_info.components[sdk].names["cmake_find_package_multi"] = "aws-sdk-cpp-" + sdk
            component_alias = f"aws-sdk-cpp-{sdk}_alias" # to emulate COMPONENTS names for find_package()
            self.cpp_info.components[component_alias].names["cmake_find_package"] = sdk
            self.cpp_info.components[component_alias].names["cmake_find_package_multi"] = sdk
            self.cpp_info.components[component_alias].requires = [sdk]

        # specific system_libs, frameworks and requires of components
        if self.settings.os == "Windows":
            self.cpp_info.components["core"].system_libs.extend([
                "winhttp", "wininet", "bcrypt", "userenv", "version", "ws2_32"
            ])
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].system_libs.append("winmm")
        else:
            self.cpp_info.components["core"].requires.extend(["libcurl::curl", "openssl::openssl"])

        if self.settings.os == "Linux":
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].requires.append("pulseaudio::pulseaudio")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["core"].system_libs.append("atomic")

        if self.options.get_safe("s3-crt"):
            self.cpp_info.components["s3-crt"].requires.append("aws-c-s3::aws-c-s3")

        if self.settings.os == "Macos":
            if self.options.get_safe("text-to-speech"):
                self.cpp_info.components["text-to-speech"].frameworks.append("CoreAudio")

        libcxx = stdcpp_library(self)
        if libcxx:
            self.cpp_info.components["core"].system_libs.append(libcxx)

        self.cpp_info.components["plugin_scripts"].requires = ["core"]
        self.cpp_info.components["plugin_scripts"].builddirs.extend([
            os.path.join(self._res_folder, "cmake"),
            os.path.join(self._res_folder, "toolchains")])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "AWSSDK"
        self.cpp_info.filenames["cmake_find_package_multi"] = "AWSSDK"
        self.cpp_info.names["cmake_find_package"] = "AWS"
        self.cpp_info.names["cmake_find_package_multi"] = "AWS"
        self.cpp_info.components["core"].names["cmake_find_package"] = "aws-sdk-cpp-core"
        self.cpp_info.components["core"].names["cmake_find_package_multi"] = "aws-sdk-cpp-core"
        self.cpp_info.components["plugin_scripts"].build_modules["cmake_find_package"] = [sdk_plugin_conf]
        self.cpp_info.components["plugin_scripts"].build_modules["cmake_find_package_multi"] = [sdk_plugin_conf]
