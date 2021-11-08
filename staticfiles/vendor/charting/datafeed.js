import {
	makeApiRequest,
	generateSymbol,
	parseFullSymbol,
} from './helpers.js';
import {
	subscribeOnStream,
	unsubscribeFromStream,
} from './streaming.js';
import { widget} from './main.js';

const lastBarsCache = new Map();


function getCookie(cname) {
      let name = cname + "=";
      let decodedCookie = decodeURIComponent(document.cookie);
      let ca = decodedCookie.split(';');
      for(let i = 0; i <ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
          c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
          return c.substring(name.length, c.length);
        }
      }
      return "";
}


const configurationData = {
//    disabled_features: ["header_widget", "header_resolutions"],
	supported_resolutions: ["1", "3", "5", "15", "30", "60", "120", "240", "360", "480", "720", "1D", "3D", "1W", "1M"],
	exchanges: [
	{
		value: 'Binance',
		name: 'Binance',
		desc: 'Binance',
	},
	{
		value: 'Coinbase',
		name: 'Coinbase',
		desc: 'Coinbase',
	},
	{
		value: 'Bitfinex',
		name: 'Bitfinex',
		desc: 'Bitfinex',
	},
	{
		// `exchange` argument for the `searchSymbols` method, if a user selects this exchange
		value: 'Kraken',

		// filter name
		name: 'Kraken',

		desc: 'Kraken',
	},
	{
		value: 'Huobi',
		name: 'Huobi',
		desc: 'Huobi',
	},
	{
		value: 'Gemini',
		name: 'Gemini',
		desc: 'Gemini',
	},
	],
	symbols_types: [{
		name: 'crypto',
		value: 'crypto',
	},
		// ...
	],
};

async function getAllSymbols() {
	const data = await makeApiRequest('data/v3/all/exchanges');
	let allSymbols = [];
    console.log('data');
    console.log(data);
	for (const exchange of configurationData.exchanges) {
		const pairs = data.Data[exchange.value].pairs;

		for (const leftPairPart of Object.keys(pairs)) {
			const symbols = pairs[leftPairPart].map(rightPairPart => {
				const symbol = generateSymbol(exchange.value, leftPairPart, rightPairPart);
				return {
					symbol: symbol.short,
					full_name: symbol.full,
					description: symbol.short,
					exchange: exchange.value,
					type: 'crypto',
				};
			});
			allSymbols = [...allSymbols, ...symbols];
		}
	}
	return allSymbols;
}

export default {
	onReady: (callback) => {
		console.log('[onReady]: Method call');
		setTimeout(() => callback(configurationData));
	},

	searchSymbols: async (
		userInput,
		exchange,
		symbolType,
		onResultReadyCallback,
	) => {
		console.log('[searchSymbols]: Method call');
		const symbols = await getAllSymbols();
		const newSymbols = symbols.filter(symbol => {
			const isExchangeValid = exchange === '' || symbol.exchange === exchange;
			const isFullSymbolContainsInput = symbol.full_name
				.toLowerCase()
				.indexOf(userInput.toLowerCase()) !== -1;
			return isExchangeValid && isFullSymbolContainsInput;
		});
		onResultReadyCallback(newSymbols);
	},

	resolveSymbol: async (
		symbolName,
		onSymbolResolvedCallback,
		onResolveErrorCallback,
	) => {
		console.log('[resolveSymbol]: Method call', symbolName);
		const symbols = await getAllSymbols();
		const symbolItem = symbols.find(({
			full_name,
		}) => full_name === symbolName);
		if (!symbolItem) {
			console.log('[resolveSymbol]: Cannot resolve symbol', symbolName);
			onResolveErrorCallback('cannot resolve symbol');
			return;
		}
		const symbolInfo = {
			ticker: symbolItem.full_name,
			name: symbolItem.symbol,
			description: symbolItem.description,
			type: symbolItem.type,
			session: '24x7',
			timezone: 'Etc/UTC',
			exchange: symbolItem.exchange,
			minmov: 1,
			pricescale: 100,
			has_intraday: true,
			has_no_volume: true,
			has_weekly_and_monthly: true,
			supported_resolutions: configurationData.supported_resolutions,
			volume_precision: 2,
			data_status: 'streaming',
		};
//        document.cookie = `symbol=${symbolName}`;
        let symbol = symbolName.split(":")[1].replace("/", "");
        // ====================== calling backend api =============================
         widget.onChartReady(function() {

//        let symbol = widget.activeChart().symbol().split(":")[1].replace("/", "");
//        let symbol = getCookie("symbol").split(":")[1].replace("/", "");

        const urlSearchParams = new URLSearchParams(window.location.search);
        const params = Object.fromEntries(urlSearchParams.entries());
        // console.log(params.limit);
        let limit;
        if (params.limit){
            limit = params.limit;
            document.cookie = `limit=${limit}`;
        } else{
            limit = getCookie('limit');
            if (limit == ""){
                limit = 1000;
            }
        };

        let interval;
        if (params.interval){
            interval = params.interval;
            widget.activeChart().setResolution(interval);
            document.cookie = `interval=${interval}`;
        } else{
            interval = getCookie('interval');
            if (interval == ""){
                interval = widget.activeChart().resolution();
                document.cookie = `interval=${interval}`;
            }
        };

        interval = String(interval);
        if (interval != '1M'){
            interval = interval.toLowerCase();
        };

         console.log('calling backend api...');
         try {
                 fetch(`http://localhost:8000/get-levels/${symbol}/${interval}/${limit}`).then(res => {
                     return res.json();
                 }).then(data => {
                 console.log('printing data...');
                 console.log(data);
                     if (data instanceof Object){
                         for (let i = 0; i < data.length; i++) {
                             widget.activeChart().createMultipointShape(
                             [{ price: data[i] }],
                                 {
                                   shape: "horizontal_line",
                                   lock: true,
                                   disableSelection: true,
                                   disableSave: true,
                                   disableUndo: true,
                                   zOrder: 'top',
                                 });
                             };
                         }
                     });
                 } catch(err) { console.error(err.message) };
    });
         // =================================================================

		console.log('[resolveSymbol]: Symbol resolved', symbolName);
		onSymbolResolvedCallback(symbolInfo);
	},

	getBars: async (symbolInfo, resolution, periodParams, onHistoryCallback, onErrorCallback) => {
		const { from, to, firstDataRequest } = periodParams;
		console.log('[getBars]: Method call', symbolInfo, resolution, from, to);
		const parsedSymbol = parseFullSymbol(symbolInfo.full_name);
		const urlParameters = {
			e: parsedSymbol.exchange,
			fsym: parsedSymbol.fromSymbol,
			tsym: parsedSymbol.toSymbol,
			toTs: to,
			limit: 2000,
		};

		const query = Object.keys(urlParameters)
			.map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
			.join('&');
		try {
			const data = await makeApiRequest(`data/histoday?${query}`);
			if (data.Response && data.Response === 'Error' || data.Data.length === 0) {
				// "noData" should be set if there is no data in the requested period.
				onHistoryCallback([], {
					noData: true,
				});
				return;
			}
			let bars = [];
			data.Data.forEach(bar => {
				if (bar.time >= from && bar.time < to) {
					bars = [...bars, {
						time: bar.time * 1000,
						low: bar.low,
						high: bar.high,
						open: bar.open,
						close: bar.close,
					}];
				}
			});
			if (firstDataRequest) {
				lastBarsCache.set(symbolInfo.full_name, {
					...bars[bars.length - 1],
				});
			}
			console.log(`[getBars]: returned ${bars.length} bar(s)`);
			onHistoryCallback(bars, {
				noData: false,
			});
		} catch (error) {
			console.log('[getBars]: Get error', error);
			onErrorCallback(error);
		}
	},

	subscribeBars: (
		symbolInfo,
		resolution,
		onRealtimeCallback,
		subscribeUID,
		onResetCacheNeededCallback,
	) => {
		console.log('[subscribeBars]: Method call with subscribeUID:', subscribeUID);
		subscribeOnStream(
			symbolInfo,
			resolution,
			onRealtimeCallback,
			subscribeUID,
			onResetCacheNeededCallback,
			lastBarsCache.get(symbolInfo.full_name),
		);

        var c_interval = getCookie('interval');
        if (resolution != c_interval){
            hit_api(resolution);
//            console.log('res_');
//            console.log('before', c_interval);
//            console.log('now', resolution);
//            document.cookie = `interval=${resolution}`;
        }

	},

	unsubscribeBars: (subscriberUID) => {
		console.log('[unsubscribeBars]: Method call with subscriberUID:', subscriberUID);
		unsubscribeFromStream(subscriberUID);
	},
};


function hit_api(resolution) {
        console.log("hit_api");
        document.cookie = `interval=${resolution}`;
        let symbol = widget.activeChart().symbol().split(":")[1].replace("/", "");

        let limit;
        limit = getCookie('limit');
        if (limit == ""){
            limit = 1000;
        };

        let interval;
        interval = String(resolution);
        if (interval != '1M'){
            interval = interval.toLowerCase();
        };

        console.log('calling backend api...');
        try {
             let url = `http://localhost:8000/get-levels/${symbol}/${interval}/${limit}`;
             console.log('url', url);
             fetch(url).then(res => {
                 return res.json();
             }).then(data => {
             console.log('printing data...');
             console.log(data);
                 if (data instanceof Object){
                     for (let i = 0; i < data.length; i++) {
                         widget.activeChart().createMultipointShape(
                         [{ price: data[i] }],
                             {
                               shape: "horizontal_line",
                               lock: true,
                               disableSelection: true,
                               disableSave: true,
                               disableUndo: true,
                               zOrder: 'top',
                             });
                         };
                     }
                 });
                 } catch(err) { console.error(err.message) };
};


function callback(){
    console.log('callbackfunc');
}