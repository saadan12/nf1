// Datafeed implementation, will be added later
import Datafeed from './datafeed.js';

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

//let symbol = getCookie("symbol");
//if (symbol == ""){
//    symbol = "Binance:BTC/USDT";
//} else{
//    symbol = symbol.split(":")[1].replace("/", "");
//}

export var widget = window.tvWidget = new TradingView.widget({
	symbol: "Binance:BTC/USDT", // default symbol
	interval: '1D', // default interval
	fullscreen: false, // displays the chart in the fullscreen mode
	container: 'tv_chart_container',
	datafeed: Datafeed,
	width: 1080,
    height: 500,
    time_frames: [],
//    preset: "mobile",
	library_path: '../charting_library_clonned_data/charting_library/',
});



widget.headerReady().then(function() {
    console.log('setLimiterValue');
    console.log(widget.chart().getPanes());
    var limitBtn = widget.createButton();
    limitBtn.addEventListener('click', function(){
        $("#limitSelector").modal();
    });
    limitBtn.textContent = 'Set Limit';

    var intervalBtn = widget.createButton();
    intervalBtn.addEventListener('click', function(){
        $("#interval").modal();
    });
    intervalBtn.textContent = 'Set Interval';

});

