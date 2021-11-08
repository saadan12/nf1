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
	fullscreen: true, // displays the chart in the fullscreen mode
	container: 'tv_chart_container',
	datafeed: Datafeed,
	library_path: '../charting_library_clonned_data/charting_library/',
//	autosize: true,
//	disabled_features: ["header_widget", "header_resolutions"],
});


widget.headerReady().then(function() {
    var limitBtn = widget.createButton();
    // limitBtn.setAttribute('title', 'Set Limit');
    limitBtn.addEventListener('click', function(){
        $("#myModal").modal();
    });
    limitBtn.textContent = 'Set Limit';

    var intervalBtn = widget.createButton();
    // intervalBtn.setAttribute('title', 'Set Limit');
    intervalBtn.addEventListener('click', function(){
        // widget.activeChart().executeActionById("changeInterval");
        $("#interval").modal();
    });
    intervalBtn.textContent = 'Set Interval';
});
