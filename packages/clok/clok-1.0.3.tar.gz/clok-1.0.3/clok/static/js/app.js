var container = document.getElementById('everything');

function ajaxget(url, onSuccess, onError) {
  return qwest.get(url).then(
    onSuccess || function() {}
  ).catch(
    onError || function() {}
  );
}

function ajaxdelete(url, onSuccess, onError) {
  return qwest.delete(url).then(
    onSuccess || function() {}
  ).catch(
    onError || function() {}
  );
}

function ajaxpost(url, data, onSuccess, onError) {
  return qwest.post(url, {'__json_data': JSON.stringify(data)}).then(
    onSuccess || function() {}
  ).catch(
    onError || function() {}
  );
}

function ajaxput(url, data, onSuccess, onError) {
  return qwest.put(url, {'__json_data': JSON.stringify(data)}).then(
    onSuccess || function() {}
  ).catch(
    onError || function() {}
  );
}

var State = {
  webradios: [],
  alarms: [],

  whatsPlaying: null,
  isPlaying: null,

  fetchWebradios: function() {
    var that = this;
    return ajaxget('api/webradios/', function(resp) {
      that.webradios = resp.webradios;
    });
  },
  deleteWebradio: function(uuid) {
    var that = this;
    return ajaxdelete('api/webradios/' + uuid, function() {
      _.remove(that.webradios, {'uuid': uuid});;
      _.remove(that.alarms, {'webradio': uuid});;
    });
  },
  addWebradio: function(data) {
    var that = this;
    return ajaxpost('api/webradios/', data, function() {
      that.webradios = that.webradios.concat([data]);
    });
  },
  editWebradio: function(data) {
    var that = this;
    return ajaxput('api/webradios/' + data.uuid, data, function() {
      var radio = _.find(State.webradios, {'uuid': data.uuid});
      _.merge(radio, data);
    });
  },

  fetchInfos: function() {
    var that = this;
    return ajaxget('api/infos/', function(resp) {
      var radio = _.find(State.webradios, {'url': resp.infos.url});
      that.whatsPlaying = (radio && radio.name) || resp.infos.url;
      that.isPlaying = resp.infos.playing;
    });
  },
  playWebradio: function(uuid) {
    var radio = _.find(State.webradios, {'uuid': uuid});
    return ajaxget('api/play/' + radio.url);
  },
  playerHandler: function() {
    var that = this;
    if (this.isPlaying) {
      return ajaxget('api/stop/', function() {
        that.isPlaying = false;
      });
    } else {
      return ajaxget('api/play/', function() {
        that.isPlaying = true;
      });
    }
  },

  fetchAlarms: function() {
    var that = this;
    return ajaxget('api/alarms/', function(resp) {
      that.alarms = resp.alarms;
    });
  },
  deleteAlarm: function(uuid) {
    var that = this;
    return ajaxdelete('api/alarms/' + uuid, function() {
      _.remove(that.alarms, {'uuid': uuid});;
    });
  },
  addAlarm: function(data) {
    var that = this;
    return ajaxpost('api/alarms/', data, function(resp) {
      that.alarms = that.alarms.concat([resp.alarm]);
    });
  },
  editAlarm: function(data) {
    var that = this;
    return ajaxput('api/alarms/' + data.uuid, data, function() {
      var alarm = _.find(State.alarms, {'uuid': data.uuid});
      _.merge(alarm, data);
    });
  },
}


// <COMPONENTS>

var NavBar = React.createClass({displayName: "NavBar",
  render: function() {
    return (
      React.createElement("div", {id: "nav"}, 
        React.createElement("a", {href: "#/alarms"}, "/alarms"), 
        React.createElement("a", {href: "#/webradios"}, "/webradios")
      )
    );
  }
});

var PlayerBar = React.createClass({displayName: "PlayerBar",
  getDefaultProps: function() {
    return {};
  },
  render: function() {
    var action = (this.props.isPlaying) ? "STOP" : "PLAY";
    var buttonClasses = "submit-button " + ((this.props.isPlaying) ? "red" : "blue") + "-button";
    if (this.props.name) {
      return (
        React.createElement("div", {id: "player"}, 
          React.createElement("span", {className: "submit-button not-a-button no-right-border"}, this.props.name), 
          React.createElement("button", {onClick: this.props.playerHandler, className: buttonClasses}, action)
        )
      );
    } else {
      return (React.createElement("div", {id: "player"}, React.createElement("span", {className: "submit-button not-a-button"}, " … ")));
    }
  }
});

var WebradioItem = React.createClass({displayName: "WebradioItem",
  playHandler: function(e) {
    e.preventDefault();
    this.props.playWebradio(this.props.webradio.uuid);
  },
  deleteWebradioHandler: function(e) {
    e.preventDefault();
    if (confirm("Do you really want to delete radio [" + this.props.webradio.name + "] ?")) {
      this.props.deleteWebradio(this.props.webradio.uuid);
    }
  },
  render: function() {
    var href = "#/webradios/edit/" + this.props.webradio.uuid;
    return (
      React.createElement("li", null, this.props.webradio.name, " − ", ' ', 
        React.createElement("a", {className: "play-link", onClick: this.playHandler, href: "#/"}, "[>]"), " | ", ' ', 
        React.createElement("a", {className: "edit-link", href: href}, "[?]"), " | ", ' ', 
        React.createElement("a", {className: "del-link", onClick: this.deleteWebradioHandler, href: "#/"}, "[X]")
      )
    );
  }
});

var WebradioList = React.createClass({displayName: "WebradioList",
  render: function() {
    var that = this;
    var liNodes = this.props.data.map(function(webradio) {
      return (
        React.createElement(WebradioItem, {webradio: webradio, deleteWebradio: that.props.deleteWebradio, playWebradio: that.props.playWebradio})
      );
    });
    return (
      React.createElement("div", {id: "main"}, 
        React.createElement("h1", null, " > Radios"), 
        React.createElement("ul", null, 
          liNodes
        ), 
        React.createElement("a", {className: "add-button", href: "#/webradios/new"}, "[+ add]")
      )
    );
  }
});

var WebradioForm = React.createClass({displayName: "WebradioForm",
  handleSubmit: function(e) {
    e.preventDefault();
    var name = this.refs.name.getDOMNode().value.trim();
    var url = this.refs.url.getDOMNode().value.trim();
    if (!name || !url) {
      return;
    }
    if (this.props.radio.uuid) { // EDIT
      var radio = _.assign(this.props.radio, {'name': name, 'url': url});
      this.props.editWebradio(radio);
    } else {
      this.props.addWebradio({'name': name, 'url': url});
    }
    window.location.hash = '#/webradios';
  },
  getDefaultProps: function() {
    return {radio: {}};
  },
  render: function() {
    var submitString = (this.props.radio.uuid) ? "EDIT" : "ADD";
    return (
      React.createElement("form", {className: "webradio-form pure-form", onSubmit: this.handleSubmit}, 
        React.createElement("input", {className: "pure-input-1 my-input-1", type: "text", ref: "name", placeholder: "Name", defaultValue: this.props.radio.name}), React.createElement("br", null), React.createElement("br", null), 
        React.createElement("input", {className: "pure-input-1 my-input-1", type: "text", ref: "url", placeholder: "Stream URL", defaultValue: this.props.radio.url}), React.createElement("br", null), React.createElement("br", null), 
        React.createElement("div", {className: "centered"}, React.createElement("input", {className: "submit-button", type: "submit", value: submitString}))
      )
    );
  }
});

var AlarmItem = React.createClass({displayName: "AlarmItem",
  deleteAlarmHandler: function(e) {
    e.preventDefault();
    if (confirm("Do you really want to delete this alarm ?")) {
      this.props.deleteAlarm(this.props.alarm.uuid);
    }
  },
  daysFormat: function() {
    var stringDays = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    var days = this.props.alarm.days.map(function(day) {
      return stringDays[day];
    });
    return days.join(',')
  },
  limitsFormat: function() {
    var begin = this.props.alarm.start;
    var end = begin + this.props.alarm.duration;
    var begin = "" + Math.floor(begin / 3600) + ":" + Math.floor(begin % 3600 / 60);
    var end = "" + Math.floor(end / 3600) + ":" + Math.floor(end % 3600 / 60);
    return begin + ' -> ' + end;
  },
  render: function() {
    var href = "#/alarms/edit/" + this.props.alarm.uuid;
    var alarmDisabled = (this.props.alarm.disabled) ? "alarm-disabled" : "";
    return (
      React.createElement("li", {className: alarmDisabled}, this.props.radio.name, " [", this.daysFormat(), "] (", this.limitsFormat(), ") − ", ' ', 
        React.createElement("a", {className: "edit-link", href: href}, "[?]"), " | ", ' ', 
        React.createElement("a", {className: "del-link", onClick: this.deleteAlarmHandler, href: "#/"}, "[X]")
      )
    );
  }
});

var AlarmList = React.createClass({displayName: "AlarmList",
  render: function() {
    var that = this;
    var liNodes = this.props.data.alarms.map(function(alarm) {
      var radio = _.find(that.props.data.webradios, {'uuid': alarm.webradio});
      return (
        React.createElement(AlarmItem, {alarm: alarm, radio: radio, deleteAlarm: that.props.deleteAlarm})
      );
    });
    return (
      React.createElement("div", {id: "main"}, 
        React.createElement("h1", null, " > Alarms"), 
        React.createElement("ul", null, 
          liNodes
        ), 
        React.createElement("a", {className: "add-button", href: "#/alarms/new"}, "[+ add]")
      )
    );
  }
});

var AlarmForm = React.createClass({displayName: "AlarmForm",
  handleSubmit: function(e) {
    e.preventDefault();
    var webradio = this.refs.webradioChoice.getDOMNode().value;
    var days = [];
    if (this.refs.optmo.getDOMNode().checked) days.push(0);
    if (this.refs.opttu.getDOMNode().checked) days.push(1);
    if (this.refs.optwe.getDOMNode().checked) days.push(2);
    if (this.refs.optth.getDOMNode().checked) days.push(3);
    if (this.refs.optfr.getDOMNode().checked) days.push(4);
    if (this.refs.optsa.getDOMNode().checked) days.push(5);
    if (this.refs.optsu.getDOMNode().checked) days.push(6);
    var start = (+this.refs.starthour.getDOMNode().value * 3600) + (+this.refs.startminute.getDOMNode().value * 60);
    var duration = +this.refs.duration.getDOMNode().value * 60;
    var disabled = this.refs.disabled.getDOMNode().checked;
    if (this.props.alarm.uuid) { // EDIT
      var alarm = _.assign(this.props.alarm, {
        'webradio': webradio, 'days': days, 'start': start, 'duration': duration, 'disabled': disabled
      });
      this.props.editAlarm(alarm);
    } else {
      this.props.addAlarm({
        'webradio': webradio, 'days': days, 'start': start, 'duration': duration, 'disabled': disabled
      });
    }
    window.location.hash = '#/alarms';
  },
  getDefaultProps: function() {
    return {alarm: {}};
  },
  render: function() {
    var that = this;
    var submitString = (this.props.alarm.uuid) ? "EDIT" : "ADD";
    var webradioOptions = this.props.webradios.map(function(webradio) {
        return (React.createElement("option", {value: webradio.uuid}, webradio.name));
    });
    return (
      React.createElement("form", {className: "alarm-form pure-form", onSubmit: this.handleSubmit}, 
        React.createElement("br", null), 
        React.createElement("label", {for: "webradio-choice"}, "Webradio : "), 
        React.createElement("select", {ref: "webradioChoice", id: "webradio-choice", defaultValue: this.props.alarm.webradio, required: true}, 
          webradioOptions
        ), 
        React.createElement("br", null), React.createElement("br", null), 

        React.createElement("label", {for: "opt-mo", class: "pure-checkbox"}, React.createElement("input", {id: "opt-mo", ref: "optmo", type: "checkbox", defaultChecked: _.indexOf(this.props.alarm.days, 0) >= 0, value: "0"}), "Mo"), 
        React.createElement("label", {for: "opt-tu", class: "pure-checkbox"}, React.createElement("input", {id: "opt-tu", ref: "opttu", type: "checkbox", defaultChecked: _.indexOf(this.props.alarm.days, 1) >= 0, value: "1"}), "Tu"), 
        React.createElement("label", {for: "opt-we", class: "pure-checkbox"}, React.createElement("input", {id: "opt-we", ref: "optwe", type: "checkbox", defaultChecked: _.indexOf(this.props.alarm.days, 2) >= 0, value: "2"}), "We"), 
        React.createElement("label", {for: "opt-th", class: "pure-checkbox"}, React.createElement("input", {id: "opt-th", ref: "optth", type: "checkbox", defaultChecked: _.indexOf(this.props.alarm.days, 3) >= 0, value: "3"}), "Th"), 
        React.createElement("label", {for: "opt-fr", class: "pure-checkbox"}, React.createElement("input", {id: "opt-fr", ref: "optfr", type: "checkbox", defaultChecked: _.indexOf(this.props.alarm.days, 4) >= 0, value: "4"}), "Fr"), 
        React.createElement("label", {for: "opt-sa", class: "pure-checkbox"}, React.createElement("input", {id: "opt-sa", ref: "optsa", type: "checkbox", defaultChecked: _.indexOf(this.props.alarm.days, 5) >= 0, value: "5"}), "Sa"), 
        React.createElement("label", {for: "opt-su", class: "pure-checkbox"}, React.createElement("input", {id: "opt-su", ref: "optsu", type: "checkbox", defaultChecked: _.indexOf(this.props.alarm.days, 6) >= 0, value: "6"}), "Su"), 
        React.createElement("br", null), React.createElement("br", null), 

        React.createElement("label", {for: "starthour"}, "Start time :"), React.createElement("br", null), 
        React.createElement("input", {id: "starthour", className: "pure-input-1-2 my-input-1 no-right-border", type: "number", ref: "starthour", placeholder: "Hour", defaultValue: Math.floor((this.props.alarm.start || 25200) / 3600)}), 
        React.createElement("input", {className: "pure-input-1-2 my-input-1", type: "number", ref: "startminute", placeholder: "Minutes", defaultValue: Math.floor((this.props.alarm.start || 1800) % 3600 / 60)}), React.createElement("br", null), React.createElement("br", null), 

        React.createElement("label", {for: "duration"}, "Duration (minutes) :"), React.createElement("br", null), 
        React.createElement("input", {id: "duration", className: "pure-input-1 my-input-1", type: "number", ref: "duration", placeholder: "Duration (minutes)", defaultValue: Math.floor((this.props.alarm.duration || 3600) / 60)}), React.createElement("br", null), React.createElement("br", null), 

        React.createElement("label", {for: "opt-disable", class: "pure-checkbox"}, React.createElement("input", {id: "opt-disable", type: "checkbox", ref: "disabled", defaultChecked: this.props.alarm.disabled}), "Disabled"), React.createElement("br", null), React.createElement("br", null), 
        React.createElement("div", {className: "centered"}, React.createElement("input", {className: "submit-button", type: "submit", value: submitString}))
      )
    );
  }
});

var App = React.createClass({displayName: "App",
  getInitialState: function() {
    return State;
  },

  fetchWebradios: function() {
    var that = this;
    State.fetchWebradios().then(function() {
      that.setState(State);
    });
  },
  deleteWebradio: function(uuid) {
    var that = this;
    State.deleteWebradio(uuid).then(function() {
      that.setState(State);
    });
  },
  addWebradio: function(data) {
    var that = this;
    State.addWebradio(data).then(function() {
      that.setState(State);
      that.fetchWebradios();
    });
  },
  editWebradio: function(data) {
    var that = this;
    State.editWebradio(data).then(function() {
      that.setState(State);
    });
  },
  playWebradio: function(uuid) {
    var that = this;
    State.playWebradio(uuid).then(function() {
      that.setState(State);
      that.fetchInfos();
    });
  },

  fetchInfos: function() {
    var that = this;
    State.fetchInfos().then(function() {
      that.setState(State);
    });
  },
  playerHandler: function() {
    var that = this;
    State.playerHandler().then(function() {
      that.setState(State);
    });
  },

  fetchAlarms: function() {
    var that = this;
    State.fetchAlarms().then(function() {
      that.setState(State);
    });
  },
  deleteAlarm: function(uuid) {
    var that = this;
    State.deleteAlarm(uuid).then(function() {
      that.setState(State);
      that.fetchWebradios();
    });
  },
  addAlarm: function(data) {
    var that = this;
    State.addAlarm(data).then(function() {
      that.setState(State);
    });
  },
  editAlarm: function(data) {
    var that = this;
    State.editAlarm(data).then(function() {
      that.setState(State);
      that.fetchWebradios();
    });
  },

  componentDidMount: function() {
    this.fetchWebradios();
    this.fetchAlarms();
    this.fetchInfos();
    State.webradiosInterval = setInterval(this.fetchWebradios, 10000);
    State.alarmsInterval = setInterval(this.fetchAlarms, 10000);
    State.infosInterval = setInterval(this.fetchInfos, 5000);
  },
  componentWillUnmount: function() {
    clearInterval(State.webradiosInterval);
    clearInterval(State.alarmsInterval);
    clearInterval(State.infosInterval);
  },

  render: function() {
    if (this.props.page === 'webradios') {
      return (
        React.createElement("div", null, 
          React.createElement(NavBar, null), 
          React.createElement(PlayerBar, {playerHandler: this.playerHandler, name: this.state.whatsPlaying, isPlaying: this.state.isPlaying}), 
          React.createElement(WebradioList, {data: this.state.webradios, deleteWebradio: this.deleteWebradio, playWebradio: this.playWebradio})
        )
      );
    } else if (this.props.page === 'webradio-add') {
      return (
        React.createElement("div", null, 
          React.createElement(NavBar, null), 
          React.createElement(PlayerBar, {playerHandler: this.playerHandler, name: this.state.whatsPlaying, isPlaying: this.state.isPlaying}), 
          React.createElement(WebradioForm, {addWebradio: this.addWebradio})
        )
      );
    } else if (this.props.page === 'webradio-edit') {
      var radio = _.find(State.webradios, {'uuid': this.props.uuid});
      return (
        React.createElement("div", null, 
          React.createElement(NavBar, null), 
          React.createElement(PlayerBar, {playerHandler: this.playerHandler, name: this.state.whatsPlaying, isPlaying: this.state.isPlaying}), 
          React.createElement(WebradioForm, {radio: radio, editWebradio: this.editWebradio})
        )
      );
    } else if (this.props.page === 'alarms') {
      var data = {'alarms': this.state.alarms, 'webradios': this.state.webradios};
      return (
        React.createElement("div", null, 
          React.createElement(NavBar, null), 
          React.createElement(PlayerBar, {playerHandler: this.playerHandler, name: this.state.whatsPlaying, isPlaying: this.state.isPlaying}), 
          React.createElement(AlarmList, {data: data, deleteAlarm: this.deleteAlarm})
        )
      );
    } else if (this.props.page === 'alarm-add') {
      return (
        React.createElement("div", null, 
          React.createElement(NavBar, null), 
          React.createElement(PlayerBar, {playerHandler: this.playerHandler, name: this.state.whatsPlaying, isPlaying: this.state.isPlaying}), 
          React.createElement(AlarmForm, {webradios: this.state.webradios, addAlarm: this.addAlarm})
        )
      );
    } else if (this.props.page === 'alarm-edit') {
      var alarm = _.find(State.alarms, {'uuid': this.props.uuid});
      return (
        React.createElement("div", null, 
          React.createElement(NavBar, null), 
          React.createElement(PlayerBar, {playerHandler: this.playerHandler, name: this.state.whatsPlaying, isPlaying: this.state.isPlaying}), 
          React.createElement(AlarmForm, {webradios: this.state.webradios, alarm: alarm, editAlarm: this.editAlarm})
        )
      );
    } else {
      return (
        React.createElement("div", null, 
          React.createElement(NavBar, null), 
          React.createElement(PlayerBar, {playerHandler: this.playerHandler, name: this.state.whatsPlaying, isPlaying: this.state.isPlaying}), 
          React.createElement("p", null, "Woops !")
        )
      );
    }
  }
});


// <VIEWS>

function webradioView() {React.render(React.createElement(App, {page: "webradios"}), container);}
function webradioAddView() {React.render(React.createElement(App, {page: "webradio-add"}), container);}
function webradioEditView(uuid) {React.render(React.createElement(App, {page: "webradio-edit", uuid: uuid}), container);}

function alarmView() {React.render(React.createElement(App, {page: "alarms"}), container);}
function alarmAddView() {React.render(React.createElement(App, {page: "alarm-add"}), container);}
function alarmEditView(uuid) {React.render(React.createElement(App, {page: "alarm-edit", uuid: uuid}), container);}

function wildcardView() {React.render(React.createElement(App, {page: "none"}), container);}


// <ROUTES>

var routes = {
  '/webradios': webradioView,
  '/webradios/new': webradioAddView,
  '/webradios/edit/:uuid': webradioEditView,

  '/alarms': alarmView,
  '/alarms/new': alarmAddView,
  '/alarms/edit/:uuid': alarmEditView,

  '/*': wildcardView
};

var router = Router(routes);
router.init();

if (window.location.hash.indexOf('/alarms') > -1)
  alarmView();
else
  webradioView();
