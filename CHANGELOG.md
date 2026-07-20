# Changelog

## [0.2.0](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.13...v0.2.0) (2026-07-20)


### Features

* add formatting commands for backend and frontend, integrate isort and eslint-plugin-simple-import-sort ([fc7e980](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/fc7e9800f18fb72471ba31f0cd6d5c8dcd20fc7c))
* add share session URL functionality with visual feedback ([4888f51](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/4888f51cd06f285894f7262007f8457d5262c0e6))
* add WebRTC connection state handling and improve UI feedback during connection ([5b83420](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/5b83420aa9285650da87dfa276cd21a1621b203f))
* enhance telemetry analysis and communication logic in Virtual Engineer ([92a91bd](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/92a91bd61fb5f8fe4464031f91fa9f16976f9826)), closes [#6](https://github.com/Tugamer89/AC-Virtual-Engineer/issues/6)
* enhance telemetry data structure with additional metrics and improve RPM display ([ef40b61](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/ef40b61675b1e7ddebfa0fb6e15a239b567cb1f8)), closes [#5](https://github.com/Tugamer89/AC-Virtual-Engineer/issues/5)
* implement timeout handling and graceful shutdown for WebRTC connections ([b8fb682](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/b8fb6828220d3ffb41a080356c34affe2665a5c1))
* integrate MQTT for WebRTC signaling and telemetry data transfer ([2e99185](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/2e99185ff660ed16382fe8b71e93738ef8e1ed64)), closes [#8](https://github.com/Tugamer89/AC-Virtual-Engineer/issues/8) [#7](https://github.com/Tugamer89/AC-Virtual-Engineer/issues/7)


### Bug Fixes

* add type hint ignore for background_tasks definition ([50f2db4](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/50f2db432a74fa051ed7da7d1f4d2e6b14a10a5b))
* add type hints for active_connections and active_channels, ignore type check for Windows event loop policy ([6362386](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/63623868e9c8f3c6c59e1d80ed1553e53b56b0ca))
* change bump-patch-for-minor-pre-major setting to false ([8e2610d](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/8e2610d31a6ab654c79f9ce4922cdcaffed39ada))
* improve channel message sending logic in broadcast_telemetry function ([230ab02](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/230ab02fcb19476b344cc82156a3e46be433f1bc))
* improve UDP connection handling and add watchdog for telemetry data ([8c3f46e](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/8c3f46e7f9152b41168a7cb5c93916983f59eaec))
* remove unnecessary whitespace in ACUDPClient class for cleaner code ([a4dad73](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/a4dad73004727b4c6b410c2049e794a09a609622))
* replace random PIN generation with secrets for better security ([7762111](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/77621118c4f29e2fc5ced14514f28d568509f36f))
* set default values for MQTT environment variables to improve connection reliability ([bbaf010](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/bbaf010b634a13d504f80205eedc692156d0e549))
* translate log messages and comments to English for consistency ([7ac79fa](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/7ac79fae495e0f452a6b2556ac5a028dda98231b))
* update telemetry data type annotations for improved clarity and type safety ([170f219](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/170f2192114fffed0aad81b1b07d6fdc598d24e8))
* update telemetry parameter type in analyze method for improved type safety ([0cb08d0](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/0cb08d020d6db08b877dc218e5b905a13ea376cb))
* update telemetry server startup message for clarity ([1a7741a](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/1a7741a3f1befbe1377905fbb22cca422cccbad1))
* update type hint ignore for background_tasks definition ([01c8e37](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/01c8e37f4e7791786a4f1ca91ab02fb32ff8d9d6))

## [0.1.13](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.12...v0.1.13) (2026-07-17)


### Bug Fixes

* update Python dependency installation to include requirements.txt ([0b9231c](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/0b9231c108c2a0382087236763ec2b82917ec2bb))

## [0.1.12](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.11...v0.1.12) (2026-07-17)


### Bug Fixes

* updated requirements.txt ([c66cabc](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/c66cabc8d0c1eebb4a0da7f1f6fcd32c07b59ca4))

## [0.1.11](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.10...v0.1.11) (2026-07-17)


### Bug Fixes

* update icon path from favicon.svg to favicon.ico in backend compile workflow ([05cc00a](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/05cc00a62aae6ec3478e62d2e2b58f40db8771b7))

## [0.1.10](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.9...v0.1.10) (2026-07-17)


### Bug Fixes

* add favicon.ico to the frontend public directory ([67a45c2](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/67a45c2bc061106cb8def46a0a33950b8a20a194))

## [0.1.9](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.8...v0.1.9) (2026-07-17)


### Bug Fixes

* moved from pip-tools to uv compile ([f8dd391](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/f8dd39108e1486eda371b08eada2a1ec5625c034))

## [0.1.8](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.7...v0.1.8) (2026-07-17)


### Bug Fixes

* update development requirements to include pefile and ensure proper hashes ([b36c11d](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/b36c11d770643ff10435a04612249c3aeb66a9fe))

## [0.1.7](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.6...v0.1.7) (2026-07-17)


### Bug Fixes

* add colorama to development requirements and update requirements files ([14ef764](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/14ef764eee9d07e63ddde7402c8d7c5eb417e54e))

## [0.1.6](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.5...v0.1.6) (2026-07-17)


### Bug Fixes

* add macholib to development requirements and update dependencies in requirements files ([ad37622](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/ad37622aa0b7da12147792ba4d11e8a099241d8d))

## [0.1.5](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.4...v0.1.5) (2026-07-17)


### Bug Fixes

* update cache dependency path and requirements file for Python dependencies ([508ef22](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/508ef226479a9be5e690572c93f0b99b45c6d655))

## [0.1.4](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.3...v0.1.4) (2026-07-17)


### Bug Fixes

* update requirements files to use minimum version specifiers ([9a5a813](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/9a5a81313d109454436d98a131ca6f365a5725ca))

## [0.1.3](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.2...v0.1.3) (2026-07-17)


### Bug Fixes

* update package versions in requirements files to specific versions ([b96ef87](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/b96ef8744c8beafd14632927e666709b533bd619))

## [0.1.2](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.1...v0.1.2) (2026-07-17)


### Bug Fixes

* add flags to actionlint for ignoring specific input errors ([dee8313](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/dee8313f9f7a6e15c34bb87044c46a31b7783871))
* add initial .yamllint configuration for YAML linting rules ([97fce24](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/97fce248b8ad869cdb24bb6cf79c4a54e81a9ba1))
* add workflow_dispatch event to CI workflow ([96912ec](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/96912ec0bfa9819e8fd54b04fc1e14d23c9cf857))
* enhance pre-commit hook for selective checks and add CI workflow for YAML validation ([7245b2e](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/7245b2e961d8d98aacbee1ceb2fc928f2c614010))
* update actionlint flags to use regex for ignoring specific input errors ([f744ccb](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/f744ccb533e2b5c0954e4f03b30ec4181d4eb2b3))
* update actions versions in CI workflow and adjust YAML formatting check ([4b73e5a](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/4b73e5a982e3d124f5e1d96145cb4a12cd7a59b9))
* update backend dependencies and sonar project configuration ([876bd05](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/876bd057bb58e2719869694c914b7c2fbcd45861))
* update cache dependency paths in CI workflows ([c38137f](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/c38137fd8664df716435cf9184cd2bd0d455dc9d))
* update pre-commit hook to ignore scripts in prettier and add .githooks to sonar.sources ([c0eec7d](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/c0eec7dc95e875ff21fde5bbc27dc8ec74b03090))
* update YAML formatting check to target specific files in CI workflow ([75d6e95](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/75d6e9591aa24ff773dba7d1d5a51379744d2e3b))
* update YAML formatting check to use npx prettier directly ([d16fff1](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/d16fff183b37f44714e39622bd88f6a1389bd2b6))

## [0.1.1](https://github.com/Tugamer89/AC-Virtual-Engineer/compare/v0.1.0...v0.1.1) (2026-07-11)


### Features

* initial commit ([9a33730](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/9a3373039ba7aa39806bfc933b9f7a0ae37e35fc))
* initialize frontend with React, Vite, and Tailwind CSS ([8c4ccd5](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/8c4ccd5e8e33ff5b5fa493d08d58b21f87f93a8c))


### Bug Fixes

* correct subprocess call in speak method to use worker script for TTS ([836add4](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/836add4568804ef57d368016cd8f69d91b59d91c))
* ensure virtual environment is activated and deactivated in pre-commit hook ([b087ec4](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/b087ec4678dd4a1d1650dd808c40c52af0414476))
* update string parsing to exclude unwanted characters in ACUDPClient and improve TTS handling in VirtualEngineerLogic ([406e564](https://github.com/Tugamer89/AC-Virtual-Engineer/commit/406e5640f8cda44517ddb9bd9ce3c5b29dd43332))
