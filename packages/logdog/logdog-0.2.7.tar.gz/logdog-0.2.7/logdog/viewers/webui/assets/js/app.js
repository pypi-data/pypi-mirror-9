(function () {
    'use strict';

    var entityMap = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': '&quot;',
        "'": '&#39;',
        "/": '&#x2F;'
    };

    function escapeHtml(string) {
        return String(string).replace(/[&<>"'\/]/g, function (s) {
            return entityMap[s];
        });
    }

    var app = angular.module('logdog.app', [
        'ui.router',
        'ui.bootstrap'
    ],
    ['$interpolateProvider', function ($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }]);

    app.run(function () {
        $(function() {$.material.init();});
    });

    app.directive('logViewer', ['$timeout', function($timeout){
        return {
            restrict: 'A',
            scope: {socket: '=', scrollToEndEnabled: '=', logViewerApi: '='},
            templateUrl: 'partial/log-viewer.html',
            link: function (scope, element, attrs) {
                var logContainer = element.find('#id-log-lines');
                var el = element[0];
                var buffer = [];
                var emptyCounter = 0;
                var isRunning = true;

                scope.logViewerApi = scope.logViewerApi || {};
                var api = scope.logViewerApi;
                api.clear = function () {
                    logContainer[0].innerHTML = "";
                };
                api.pause = function () {
                    scope.socket.pause();
                    isRunning = false;
                };
                api.resume = function () {
                    scope.socket.resume();
                    isRunning = true;
                };

                scope.socket.on(scope.socket.events.MSG, function(event){
                    if (isRunning) {
                        buffer.push(JSON.parse(event.data));
                    }
                });

                function scrollToEnd () {
                    if (scope.scrollToEndEnabled) {
                        el.scrollTop = el.scrollHeight;
                    }
                }

                function formatMessage (message, noEscape) {
                    if (message && (typeof message.msg !== 'undefined')) {
                        var msg = message.msg;
                        msg = noEscape ? msg : escapeHtml(msg);
                        return (
                            '<div data-source="' + escapeHtml(message.src) + '">'
                                + msg.trimRight()
                            + '</div>'
                        );
                    }
                    return message;
                }

                function appendLogContainer (buf, noEscape) {
                    if (angular.isArray(buf)) {
                        angular.forEach(buf, appendLogContainer);
                    } else {
                        try {
                            logContainer.append(formatMessage(buf, noEscape));
                        } catch (e) {
                            logContainer.append(buf);
                            console.log(e);
                        }
                    }
                }

                var dumpInterval = 100;
                function dumpLog () {
                    if (buffer.length) {
                        var buf = buffer;
                        buffer = [];
                        emptyCounter = 60 * 1000 / dumpInterval;
                        appendLogContainer(buf);
                        scrollToEnd();
                    } else {
                        if (emptyCounter > 0) {
                            emptyCounter--;
                            if (emptyCounter == 0) {
                                var msg = '<hr><div class="text-center text-info">['
                                           + new Date()
                                           + '] New messages will be below.</div><hr>';
                                appendLogContainer(msg, true);
                                scrollToEnd();
                            }
                        }
                    }
                    $timeout(dumpLog, dumpInterval);
                }


                function _activate () {
                    $timeout(dumpLog, dumpInterval);
                }

                _activate();
            }
        }
    }]);

    app.service('Socket', ['$timeout', function ($timeout) {
        return function (url, reconnectDelay, maxReconnectDelay) {
            var callbacks = {
                'open': [],
                'message': [],
                'error': [],
                'close': []
            };

            var events = {
                'OPEN': 'open',
                'MSG': 'message',
                'ERR': 'error',
                'CLOSE': 'close'
            };

            var pause = false;

            var handleEvent = function (type, event) {
                if (pause) return;
                angular.forEach(callbacks[type], function (callback) {
                    callback(event);
                });
            };

            var ws = null;

            reconnectDelay = reconnectDelay || 1000;
            maxReconnectDelay = maxReconnectDelay || 32000;
            function initSocket() {
                ws = new WebSocket(url);

                ws.onopen = function (event) {
                    console.log('socket open');
                    handleEvent(events.OPEN, event);
                    reconnectDelay = 1000;
                };

                ws.onmessage = function (event) {
                    console.log('socket message');
                    handleEvent(events.MSG, event);
                };

                ws.onerror = function (event) {
                    console.log('socket error');
                    handleEvent(events.ERR, event);
                };

                ws.onclose = function (event) {
                    console.log('socket close');
                    console.log('trying to reconnect... Next try in ' + reconnectDelay + 'ms');
                    handleEvent(events.CLOSE, event);
                    $timeout(initSocket, reconnectDelay);
                    reconnectDelay *= 2;
                    reconnectDelay = reconnectDelay > maxReconnectDelay ? maxReconnectDelay : reconnectDelay;
                };

                return ws;
            }

            return {
                'events': events,
                'ws': initSocket(),
                'on': function(eventType, cb){
                    callbacks[eventType].push(cb);
                },
                'off': function(eventType){
                    delete callbacks[eventType];
                },
                'pause': function(){pause = true;},
                'resume': function(){pause = false;}
            }

        };
    }]);

    app.controller('LogViewCtl', ['$scope', 'Socket', function($scope, Socket){
        $scope.socket = Socket('ws://' + location.host + '/ws/logs');
        $scope.scrollToEndEnabled = true;
        $scope.isRunning = true;
        $scope.logViewerApi = {};
        $scope.onStartStop = function () {
            $scope.isRunning = !$scope.isRunning;
            $scope.logViewerApi[$scope.isRunning ? 'resume' : 'pause']();
        };
        $scope.onClear = function () {
            $scope.logViewerApi.clear && $scope.logViewerApi.clear();
        };
    }]);
})();