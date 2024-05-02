#!/bin/bash 

# Download nginx images
download() {
    if [ ! -d images ]; then
        mkdir images
    fi
    curl -o images/`basename $1` $1
    echo "images/`basename $1`をダウンロードしました!"
}

main() {
    if [ $1 ]; then
        download $1
    else
        echo "alert.txtからURLを選択して、再度実行してください。"
        echo "------alert.txt------"
        cat alert.txt
        echo "------alert.txt------"
        # サンプル用にalert.txtの1行目を取得
        sample_url=`head -n 1 alert.txt`
        echo "------Sample script------"
        echo "./downloads.sh $sample_url"
    fi
}

main $1