
const csv=require('csvtojson');
const fs = require('fs');

const debug = false;

const csvFilePath='./result/r_stats.csv';
const checkPath = './result/check.dat'

const path = './result/score.dat';

const warnFilePath = './result/check_warn.dat';

const table = {
    "GET:/categories": {
        correction: 0.7,
        num: 0,
    },
    "POST:/files": {
        correction: 1.4,
        num: 0,
    },
    "GET:/record-views/allActive": {
        correction: 1.2,
        num: 0,
    },
    "GET:/record-views/allClosed": {
        correction: 1.3,
        num: 0,
    },
    "GET:/record-views/mineActive": {
        correction: 1.2,
        num: 0,
    },
    "GET:/record-views/tomeActive": {
        correction: 1.4,
        num: 0,
    },
    "POST:/records": {
        correction: 1.2,
        num: 0,
    },
    "GET:/records/[recordId]": {
        correction: 1.0,
        num: 0,
    },
    "PUT:/records/[recordId]": {
        correction: 0.8,
        num: 0,
    },
    "GET:/records/[recordId]/comments": {
        correction: 0.9,
        num: 0,
    },
    "POST:/records/[recordId]/comments": {
        correction: 1.0,
        num: 0,
    },
    "GET:/records/[recordId]/files/[itemId]": {
        correction: 1.0,
        num: 0,
    },
    "GET:/records/[recordId]/files/[itemId]/thumbnail": {
        correction: 1.0,
        num: 0,
    },
}

let maxSuccess = 0;
let minSuccess = 65535;

const mylog = (m) => {
    if (!debug) {
        return;
    }
    console.log(m);
}

const main = async() => {

    const checkStr = fs.readFileSync(checkPath, 'utf-8');

    if (Number(checkStr) !== 1) {
        console.log('INFO: APIテストのPASSが確認できません。');
        fs.writeFileSync(path, String(0));
        return;
    }

    const jsonObj = await csv().fromFile(csvFilePath)
    let baseScore = 0;
    if (!Array.isArray(jsonObj) || jsonObj.length < 1) {
        console.log('ERROR: LocustのCSV解析に失敗しました。');
        fs.writeFileSync(path, 'ERROR: LocustのCSV解析に失敗しました。');
        return
    }
    for (const x of jsonObj) {
        if (x.Name === 'Aggregated') {
            continue;
        }
        if (table[`${x.Type}:${x.Name}`] === undefined) {
            console.log(`WARN: 解析できない結果が含まれています。:${x.Type}:${x.Name}`);
            continue;
        }
        table[`${x.Type}:${x.Name}`].num = Number(x['Request Count']) - Number(x['Failure Count']);
    }

    mylog(table);

    for (const k of Object.keys(table)) {
        const num = table[k].num;

        if (num > maxSuccess) {
            maxSuccess = num;
        }
        if (num < minSuccess) {
            minSuccess = num;
        }
        const correction = table[k].correction;
        let apiScore = num * correction;

        if (k === 'GET:/categories') {
            const limit = (table["POST:/records"].num + 1) * 4;
            if (num > limit) {
                console.log(`INFO: カテゴリー一覧取得の結果を補正します。limit: ${limit}`);
                apiScore = limit * correction;
            }
        }
        baseScore += apiScore;
    }

    let baseScoreInt = Math.ceil(baseScore); //ベーススコアは切り上げ。

    const maxMinRatio = Math.floor(maxSuccess / (minSuccess + 1));
    const diff = maxMinRatio - 50;
    let minusSum = 0;
    if (diff > 0) {
        console.log(`INFO: 最大最小成功数比率に基づき結果を補正します。 max:${maxSuccess}: min:${minSuccess}`);
        for (let i = 0; i < diff; i++) {
            const minus = Math.floor(baseScoreInt * 0.01);
            if (minus < 1) {
                break;
            }
            baseScoreInt -= minus;
            minusSum += minus;
        }
    }
    if (minusSum > 0) {
        console.log(`INFO: 最大最小成功数比率による減点: ${minusSum} 点`);
    }
    try {
        const warn = fs.readFileSync(warnFilePath, 'utf-8');
        if (warn !== 'ok') {
            console.log(`WARN: 細部チェックに問題がありました。考慮される場合があります。 message: ${warn}`);
        }
    } catch(e) {
        console.log('WARN: warnの検証に失敗しました。')
    }

    fs.writeFileSync(path, String(baseScoreInt));

}


main()