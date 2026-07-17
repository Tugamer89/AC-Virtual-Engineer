# Changelog

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
