console.log("HELL")
window.TrelloPowerUp.initialize({
  "card-buttons": function (t, options) {
    var context = t.getContext();
    console.log(JSON.stringify(context, null, 2));
    return [
      {
        icon: "https://github.com/walkxcode/dashboard-icons/blob/main/png/adblock.png",
        text: "Mirror/sync",
        callback: function (t) {
          return t.popup({
            title: "Mirror/sync",
            url: t.signUrl("/test"),
          });
        },
      },
    ];
  },
});
