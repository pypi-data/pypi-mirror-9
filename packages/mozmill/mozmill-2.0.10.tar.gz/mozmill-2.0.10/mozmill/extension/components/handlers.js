/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, you can obtain one at http://mozilla.org/MPL/2.0/. */

const Cc = Components.classes;
const Ci = Components.interfaces;
const Cu = Components.utils;

// Import global modules
Cu.import("resource://gre/modules/XPCOMUtils.jsm");
Cu.import("resource://gre/modules/Services.jsm");

// Import local modules
Cu.import('resource://mozmill/modules/assertions.js');
Cu.import("resource://jsbridge/modules/Events.jsm");


/**
 * XPCOM component to setup necessary listeners for Mozmill.
 */
function MozmillHandlers() {

}

MozmillHandlers.prototype = {
  classDescription: "MozmillHandlers",
  classID: Components.ID("{06aff66f-4925-42e1-87f8-acaeaa22cabf}"),
  contractID: "@mozilla.org/mozmill/handlers;1",
  QueryInterface: XPCOMUtils.generateQI([Ci.nsIObserver]),

  _xpcom_categories: [{category: "profile-after-change"}],

  /**
   * Handler for registered observer notifications.
   *
   * @param {String} aSubject
   *        Subject of the observer message (not used)
   * @param {String} aTopic
   *        Topic of the observer message
   * @param {Object} aData
   *        Data of the observer message (not used)
   */
  observe: function MozmillHandlers_observe(aSubject, aTopic, aData) {
    switch (aTopic) {
      // The server cannot be started before the ui is shown. That means
      // we also have to register for the final-ui-startup notification.
      case "profile-after-change":
        Services.console.registerListener(ConsoleObserver);
        Services.obs.addObserver(this, "quit-application", false);
        break;
      case "quit-application":
        Services.obs.removeObserver(this, "quit-application", false);
        Services.console.unregisterListener(ConsoleObserver);
        break;
    }
  }
}


var ConsoleObserver = {
  errorRegEx : /\[.*(\WError|\WException).*(chrome|resource):\/\/(mozmill|jsbridge).*/i,
  externalFileRegEx :  /.*\.js -> file:\/\/\/.*/,

  observe: function (aSubject, aTopic, aData) {
    var msg = aSubject.message;

    // If the message is not related to one of our extensions forget about it
    if (!msg.contains('mozmill') && !msg.contains('jsbridge')) {
      return
    }

    // Only care about errors and exceptions but not warnings and other messages
    if (msg.match(this.errorRegEx)) {
      // If there is an exception happening in a background thread caused by a
      // test, don't raise a framework failure because the error gets forwarded
      // through the console service.
      if (msg.match(this.externalFileRegEx)) {
        new Expect().fail(msg);
      }
      else {
        Events.fireEvent("mozmill.frameworkFail", {message: msg});
        Events.fireEvent("mozmill.shutdown", {
          'user': false,
          'restart': false,
          'resetProfile': false
        });

        // Quit the application and do not wait until a timeout happens
        Services.startup.quit(Ci.nsIAppStartup.eAttemptQuit);
      }
    }
  }
};

const NSGetFactory = XPCOMUtils.generateNSGetFactory([MozmillHandlers]);
