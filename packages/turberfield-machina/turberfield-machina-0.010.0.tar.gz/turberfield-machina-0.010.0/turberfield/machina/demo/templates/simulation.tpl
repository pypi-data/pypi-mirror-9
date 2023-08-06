<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>{{info.get("title", "Turberfield")}}</title>
<link rel="stylesheet" href="/css/animations.css" />
<link rel="stylesheet" href="/css/base-min.css" />
<link rel="stylesheet" href="/css/pure-min.css" media="screen" />
<link rel="stylesheet" href="/css/grids-responsive-min.css" media="screen" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
% if info['refresh']:
<meta http-equiv="refresh" content="{{info['refresh']}}" />
% end
</head>
<body>
% include("gainsborough_square.tpl")
<%
location = {
"A": "at stop A",
"B": "at stop B",
"C": "at stop C",
"Bus": "on the bus",
}.get(info['location'], "not yet sure where you are..")

neighbours = ', '.join([i[0] for i in items]) or "nobody"
%>
<div class="pure-g">
    <div class="pure-u-lg-1-12">
    </div>
    <div class="pure-u-1 pure-u-lg-5-6">
    <p>You are {{location}}. You see {{neighbours}}.</p>
    </div>
    <div class="pure-u-lg-1-12">
    </div>
</div>

<ul data-bind="foreach: events" style="list-style-type: none;">
  <li>
    <dl data-bind="visible: false">
        <dt data-bind="text: label"></dt>
        <dd data-bind="text: uuid"></dd>
        <dd data-bind="text: closes"></dd>
    </dl>
    <form data-bind="attr: {
    action: _links[0].typ.replace('{}', _links[0].ref),
    class: 'pure-form',
    method: _links[0].method
    }">
    <fieldset>
    <legend data-bind="text: _links[0].name"></legend>
    <label data-bind="text: 'Transfer to ' + label + ' '"></label>
    <input data-bind="attr: {
    name: _links[0].parameters[0][0],
    value: _links[0].parameters[0][3][0],
    type: 'hidden'
    }" />
    <button
    class="pure-button pure-button-primary"
    type="submit"
    data-bind="text: _links[0].prompt">
    </button>
    </fieldset>
    </form>
  </li>
</ul>

<script type="text/javascript" src="/js/jquery-2.1.1.js"></script>
<script type="text/javascript" src="/js/knockout-3.2.0.js"></script>
<script type="text/javascript">

var viewModel = {
    positions: ko.observableArray(),
    events: ko.observableArray()
}

var checkPositions = function() {

    $.getJSON('/data/positions.json', function(data) {
        viewModel.positions(data.items);
    });


};

var checkEvents = function() {

    $.getJSON('/events/{{info.get("actor", "")}}', function(data) {
        viewModel.events(data.items);
    });


};

ko.applyBindings(viewModel);
setInterval(checkPositions, {{info.get("interval", 500)}});
setInterval(checkEvents, {{info.get("interval", 500)}});

</script>

</body>
</html>
