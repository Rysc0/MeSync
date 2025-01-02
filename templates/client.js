console.log("HELL")
TrelloPowerUp.initialize({
  "card-buttons": function (t, options) {
    return [
      {
        icon: "https://github.com/walkxcode/dashboard-icons/blob/main/png/adblock.png",
        text: "Mirror/sync",
        callback: function (t) {
          return t.popup({
            title: "Mirror/sync",
            url: "test.html",
          });
        },
      },
    ];
  },
});
