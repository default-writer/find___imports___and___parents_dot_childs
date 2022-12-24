#!/usr/bin/env bash
set -e

uid=$(id -u)

if [ "${uid}" -eq 0 ]; then
    echo "Please run as user"
    exit
fi

pwd=$(pwd)

array="undefined"
clean="undefined"

install="$1"
remove="$2"

case "${remove}" in

    "")
        ;;

    "--clean") # cleans up directories before build
        clean="--clean"
        ;;

    *)
        commands=$(cat $0 | sed -e 's/^[ \t]*//;' | sed -e '/^[ \t]*$/d' | sed -n -e 's/^"\(.*\)".*#/    \1:/p' | sed -n -e 's/: /:\n        /p')
        script="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
        help=$(\
cat << EOF
Builds main test executables into build folder
Usage: ${script} <option> [--clean]
${commands}
EOF
)
        echo "${help}"
        exit
        ;;

esac

case "${install}" in

    "--playground") # builds and runs '-playground' target
        array=("-playground")
        ;;

    "--alloc") # builds and runs '-alloc' target
        array=("-alloc")
        ;;

    "--experimental") # builds and runs '-experimental' target
        array=("-experimental")
        ;;

    "--micro") # builds and runs '-micro' target
        array=("-micro")
        ;;

    "--light") # builds and runs '-light' target
        array=("-light")
        ;;

    "--all") # builds and runs all targets
        array=("" "-light" "-micro" "-experimental" "-alloc" "-playground")
        ;;

    *)
        commands=$(cat $0 | sed -e 's/^[ \t]*//;' | sed -e '/^[ \t]*$/d' | sed -n -e 's/^"\(.*\)".*#/    \1:/p' | sed -n -e 's/: /:\n        /p')
        script="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
        help=$(\
cat << EOF
Builds binaries with code converage information ('lcov.info')
Usage: ${script} <option> [--clean]
${commands}
EOF
)
        echo "${help}"
        exit
        ;;

esac

[ ! -d "${pwd}/coverage" ] && mkdir "${pwd}/coverage"

if [ "${clean}" == "--clean" ]; then
    rm -rf "${pwd}/coverage"
    mkdir "${pwd}/coverage"
fi

for m in "${array[@]}"; do
    rm -f "${pwd}/coverage/main${m}.lcov"
done

find "${pwd}/coverage" -name "main*.gcda" -delete
find "${pwd}/coverage" -name "main*.gcno" -delete

cmake \
    -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE \
    -DCMAKE_BUILD_TYPE:STRING=Debug \
    -DCMAKE_C_COMPILER:FILEPATH=/usr/bin/gcc \
    -DCMAKE_CXX_COMPILER:FILEPATH=/usr/bin/g++ \
    -DCODE_COVERAGE:BOOL=TRUE \
    -DLCOV_PATH=$(which lcov) \
    -DGENHTML_PATH==$(which genhtml) \
    -S"${pwd}" \
    -B"${pwd}/cmake" \
    -G "Unix Makefiles"

## compile with coverage metadata
for m in "${array[@]}"; do
    cmake --build "${pwd}/cmake" --target "main${m}"

    "${pwd}/cmake/main${m}"
    lcov --capture --directory "${pwd}/cmake/" --output-file "${pwd}/coverage/main${m}.lcov"
    lcov --remove "${pwd}/coverage/main${m}.lcov" "${pwd}/src/rexo/*" -o "${pwd}/coverage/main${m}.lcov"
    rm -rf "${pwd}/coverage/main${m}"
done

find "${pwd}/coverage" -name "main*.gcda" -delete
find "${pwd}/coverage" -name "main*.gcno" -delete
find "${pwd}/coverage" -name "main*.lcov" -exec echo -a {} \; | xargs lcov -o "${pwd}/coverage/lcov.info"
find "${pwd}/coverage" -name "main*.lcov" -delete

cd "${pwd}"