/** @jsx React.DOM */
/**
 * Copyright (c) 2014, Facebook, Inc.
 * All rights reserved.
 *
 *  This source code is licensed under the BSD-style license found in the
 *  LICENSE file in the root directory of this source tree. An additional grant
 *  of patent rights can be found in the PATENTS file in the same directory.
 */



/** https://gist.github.com/NV/8622188 **/
/**
 * RecursiveLinkStateMixin is a LinkState alternative that can update keys in
 * a dictionnary recursively.
 * You can either give it a string of keys separated by a underscore (_)
 * or a list of keys
 */
var RecursiveLinkStateMixin = {
    linkState: function (path) {
        function setPath (obj, path, value) {
            var leaf = resolvePath(obj, path);
            leaf.obj[leaf.key] = value;
        }

        function getPath (obj, path) {
            var leaf = resolvePath(obj, path);
            return leaf.obj[leaf.key];
        }

        function resolvePath (obj, keys) {
            if (typeof keys === 'string') {
                keys = keys.split('_');
            }
            var lastIndex = keys.length - 1;
            var current = obj;
            for (var i = 0; i < lastIndex; i++) {
                var key = keys[i];
                current = current[key];
            }
            return {
                obj: current,
                key: keys[lastIndex]
            };
        }

        return {
            value: getPath(this.state, path),
            requestChange: function(newValue) {
                setPath(this.state, path, newValue);
                this.forceUpdate();
            }.bind(this)
        };
    }
};

var IdentifyableObject = {
    getIdentifier: function () {
        return this.props.params.join('_');
    },
};

var atc_status = {
    OFFLINE: 0,
    ACTIVE: 1,
    INACTIVE: 2,
    OUTDATED: 3,
};


function handleAPI(link_state, callback) {
    return function(rc) {
        /* 2XX error codes are OK */
        if (rc.status < 300 && rc.status >= 200) {
            if (callback !== undefined) {
                callback(rc);
            }    
        } else {
            err = false;
            t = typeof rc.json;
            if (t === 'undefined') {
                err = {
                    detail: "Could not complete request due to server error.",
                }
            } else if (t === 'string') {
                s = rc.json

                /* trim off the first line */
                s = s.trim().substring(s.length, s.indexOf('\n'))

                /* take the second line as the error message */
                s = s.trim().substring(0, s.indexOf('\n'))

                err = {
                    detail: s,
                };
            } else if (t === 'object') {
                err = rc.json;
            }

            if (err) {
                link_state('errorMsg').requestChange(err);
            } else {
                console.log("Not sure what to do with error value " + t + " '" + rc.json + "'");
            }
        }
    }
}


var ShapingButton = React.createClass({
    render: function () {
        button_values = [
            {
                message: "ATC is not running",
                css: "danger",
            },
            {
                message: "Turn Off",
                css: "success",
            },
            {
                message: "Turn On",
                css: "default",
            },
            {
                message: "Update Shaping",
                css: "warning",
            },
        ];

        content = button_values[this.props.status];
        return (
            <button type="button" id={this.props.id} className={"btn btn-" + content.css} disabled={this.props.status == atc_status.OFFLINE} onClick={this.props.onClick}>
                {content.message}
            </button>
        );
    }
});


var LinkShapingNumberSetting = React.createClass({
    mixins: [IdentifyableObject],
    render: function () {
        id = this.getIdentifier();
        link_state = this.props.link_state("settings_" + id);
        return (
            <div className="form-group">
                <label htmlFor={id} className="col-sm-3 control-label">{this.props.text}</label>
                <div className="col-sm-9">
                    <input type="number" defaultValue={link_state.value} className="form-control" id={id} placeholder={this.props.placeholder} min="0" max={this.props.max_value} valueLink={link_state} />
                </div>
            </div>
        )
    }
});


var LinkShapingPercentSetting = React.createClass({
    render: function () {
        return (
            <LinkShapingNumberSetting input_id={this.props.input_id} text={this.props.text} placeholder="In %" link_state={this.props.link_state} max_value="100" />
        )
    }
});


var CollapseableInputList = React.createClass({
    render: function () {
        return (
            <fieldset className="accordion-group">
                <legend>{this.props.text}</legend>
                {this.props.children}
            </fieldset>
        );
    }
});


var CollapseableInputGroup = React.createClass({
    mixins: [IdentifyableObject],
    getInitialState: function () {
        return {collapsed: true};
    },

    handleClick: function (e) {
        this.setState({collapsed: !this.state.collapsed})
    },

    render: function () {
        id = this.getIdentifier();
        var text = this.state.collapsed ? 'Show more' : 'Show less';
        return (
            <div>
                <div className="accordion-heading">
                    <a className="accordion-toggle" data-toggle="collapse" data-target={"#" + id} href="#" onClick={this.handleClick}>{text}</a>
                </div>
                <div className="accordion-body collapse" id={id}>
                    <div className="accordion-inner">
                        {this.props.children}
                    </div>
                </div>
            </div>
        );
    }
});


var LinkShapingSettings = React.createClass({
    render: function () {
        d = this.props.direction;
        return (
            <div className="well" id={d + "_well"}>
                <h3>{d + "link"}</h3>
                <div className="form-horizontal accordion">
                    <LinkShapingNumberSetting params={[d, "rate"]} text="Bandwidth" placeholder="in kbps" link_state={this.props.link_state} />
                    <CollapseableInputList text="Latency">
                        <LinkShapingNumberSetting params={[d, "delay", "delay"]} text="Delay" placeholder="in ms" link_state={this.props.link_state} />
                        <CollapseableInputGroup params={[d, "delay", "collapse"]}>
                            <LinkShapingNumberSetting params={[d, "delay","jitter"]} text="Jitter" placeholder="in %" link_state={this.props.link_state} />
                            <LinkShapingNumberSetting params={[d, "delay", "correlation"]} text="Correlation" placeholder="in %" link_state={this.props.link_state} />
                        </CollapseableInputGroup>
                    </CollapseableInputList>
                    <CollapseableInputList text="Loss">
                        <LinkShapingNumberSetting params={[d, "loss", "percentage"]} text="Percentage" placeholder="in %" link_state={this.props.link_state} />
                        <CollapseableInputGroup params={[d, "loss", "collapse"]}>
                            <LinkShapingNumberSetting params={[d, "loss", "correlation"]} text="Correlation" placeholder="in %" link_state={this.props.link_state} />
                        </CollapseableInputGroup>
                    </CollapseableInputList>
                    <CollapseableInputList text="Corruption">
                        <LinkShapingNumberSetting params={[d, "corruption", "percentage"]} text="Percentage" placeholder="in %" link_state={this.props.link_state} />
                        <CollapseableInputGroup params={[d, "corruption", "collapse"]}>
                            <LinkShapingNumberSetting params={[d, "corruption", "correlation"]} text="Correlation" placeholder="in %" link_state={this.props.link_state} />
                        </CollapseableInputGroup>
                    </CollapseableInputList>
                    <CollapseableInputList text="Reorder">
                        <LinkShapingNumberSetting params={[d, "reorder", "percentage"]} text="Percentage" placeholder="in %" link_state={this.props.link_state} />
                        <CollapseableInputGroup params={[d, "reorder", "collapse"]}>
                            <LinkShapingNumberSetting params={[d, "reorder", "correlation"]} text="Correlation" placeholder="in %" link_state={this.props.link_state} />
                            <LinkShapingNumberSetting params={[d, "reorder", "gap"]} text="Gap" placeholder="integer" link_state={this.props.link_state}/>
                        </CollapseableInputGroup>
                    </CollapseableInputList>
                </div>
            </div>
        );
    }
});


var ShapingSettings = React.createClass({
    render: function () {
        return (
            <div>
                <div className="col-md-6">
                    <LinkShapingSettings direction="up" link_state={this.props.link_state} />
                </div>
                <div className="col-md-6">
                    <LinkShapingSettings direction="down" link_state={this.props.link_state} />
                </div>
            </div>
        );
    }
});


var Profile = React.createClass({
    getInitialState: function() {
        return {
            name: "",
        };
    },

    handleClick: function() {
        this.props.link_state("settings").requestChange(
            new AtcSettings().mergeWithDefaultSettings(this.props.profile.content)
        );
    },

    updateName: function(event) {
        this.setState({name: event.target.value});
    },

    removeProfile: function() {
        this.props.link_state("client").value.delete_profile(handleAPI(this.props.link_state, this.props.refreshProfiles), this.props.profile.id);
    },

    render: function () {
        return (
            <div className="list-group-item row">
                <span className="col-sm-6 text-center vcenter"><kbd>{this.props.profile.name}</kbd></span>
                <span className="col-sm-2 text-center vcenter">{this.props.profile.content.up.rate} kbps</span>
                <span className="col-sm-2 text-center vcenter">{this.props.profile.content.down.rate} kbps</span>
                <button className="col-sm-1 btn btn-info vcenter" onClick={this.handleClick}>Select</button>
                <button className="col-sm-1 btn btn-danger vcenter" onClick={this.removeProfile}>Delete</button>
            </div>);
    }
});


var ProfileList = React.createClass({
    render: function() {
        if (this.props.profiles.length == 0) {
            return false;
        }

        var profileNodes = this.props.profiles.map(function (profile) {
            return (
                <Profile refreshProfiles={this.props.refreshProfiles} link_state={this.props.link_state} action='delete' profile={profile} />
            );
        }.bind(this));

        return (
            <div>
                <h3>Existing Profiles</h3>
                <p>
                    Select a profile from the list below to use it.
                </p>
                <div className="list-group">
                    <div className="list-group-item row">
                        <span className="col-sm-6 text-center vcenter"><b>Name</b></span>
                        <span className="col-sm-2 text-center vcenter"><b>Up Rate</b></span>
                        <span className="col-sm-2 text-center vcenter"><b>Down Rate</b></span>
                        <span className="col-sm-1 text-center vcenter"></span>
                        <span className="col-sm-1 text-center vcenter"></span>
                    </div>

                    {profileNodes}
                </div>
            </div>
        );
    }
});


var CreateProfileWidget = React.createClass({
    getInitialState: function() {
        return {
            name: ""
        };
    },

    updateName: function(event) {
        this.setState({name: event.target.value});
    },

    newProfile: function() {
        var settings = this.props.link_state('settings').value;
        if (settings.down.rate == null &&
            settings.up.rate == null) {
            this.props.link_state('errorMsg').requestChange({detail:"Enter your settings below and click Create to save the profile."});
            return;
        }
        if (this.state.name == "") {
            this.props.link_state('errorMsg').requestChange({detail:"You must give this new profile a name."});
            return;
        }

        var addProfile = function() {
            this.setState({
                name: "",
            });
            this.props.refreshProfiles();
        }.bind(this);

        var profile = {
            name: this.state.name,
            content: settings
        };
        console.log("Creating profile " + profile.name);
        this.props.link_state("client").value.new_profile(handleAPI(this.props.link_state, addProfile), profile);
    },

    render: function() {
        return (
            <div>
                <h3>New Profile</h3>
                <p>
                    Enter a name and click "Create" to save a new profile.
                </p>
                <input type="text" className="form-control" placeholder="Profile Name" onChange={this.updateName}/>
                <button className="col-sm-2 btn btn-success" onClick={this.newProfile}>Create</button>
            </div>
        );
    },
});


var ProfilePanel = React.createClass({
    render: function () {
        return (
            <div className="panel panel-default">
                <div className="panel-body">
                    <ProfileList refreshProfiles={this.props.refreshProfiles} link_state={this.props.link_state} profiles={this.props.profiles}/>

                    <CreateProfileWidget refreshProfiles={this.props.refreshProfiles} link_state={this.props.link_state}/>
                </div>
            </div>
        );
    }
});


var ErrorBox = React.createClass({
    render: function () {
        var errors = this.props.error.detail;
        if (typeof this.props.error.detail === 'string') {
            errors = Array(this.props.error.detail);
        } else if (typeof this.props.error.detail === 'object') {
            errors = this.props.error.detail;
        }
        var errorNodes = errors.map(function(error) {
            return (
                <li>{error}</li>
            );
        });
        return (
            <div className="alert alert-danger" role="alert">
                <ul>
                {errorNodes}
                </ul>
            </div>
        )
    }
});


var Atc = React.createClass({
    mixins: [RecursiveLinkStateMixin],
    getInitialState: function() {
        return {
            client: new AtcRestClient(this.props.endpoint),
            settings: new AtcSettings().getDefaultSettings(),
            current_settings: new AtcSettings().getDefaultSettings(),
            status: atc_status.OFFLINE,
            errorMsg: "",
            profiles: [],
        };
    },

    componentDidMount: function() {
        this.getCurrentShaping();
        /** FIXME we are calling getCurrentShaping to make sure that
         * current_settings === settings.... let's be smarter than that.
         */
        this.getCurrentShaping();
        this.getProfiles();
    },

    handleClick: function(e) {
        if (e.type == "click") {
            if (this.state.status == atc_status.ACTIVE) {
                this.unsetShaping();
            } else if (this.state.status == atc_status.INACTIVE) {
                this.setShaping();
            }
        }
    },

    updateClick: function(e) {
        if (e.type == "click") {
            this.setShaping();
        }
    },

    hasChanged: function() {
        /* TODO: improve object comparaison e.g null == "", 1 == "1"*/
        function objectEquals(x, y) {
            if (typeof(x) === 'number') {
                x = x.toString();
            }
            if (typeof(y) === 'number') {
                y = y.toString();
            }
            if (typeof(x) != typeof(y)) {
                return false;
            }

            if (Array.isArray(x) || Array.isArray(y)) {
                return x.toString() === y.toString();
            }

            if (x === null && y === null) {
                return true;
            }

            if (typeof(x) === 'object' && x !== null) {
                x_keys = Object.keys(x);
                y_keys = Object.keys(y);
                if (x_keys.sort().toString() !== y_keys.sort().toString()) {
                    console.error('Object do not have the same keys: ' +
                        x_keys.sort().toString() + ' vs ' +
                        y_keys.sort().toString()
                    );
                    return false;
                }
                equals = true;
                for (key of x_keys) {
                    equals &= objectEquals(x[key], y[key]);
                }
                return equals;
            }
            return x.toString() === y.toString();
        }
        return !objectEquals(this.state.settings, this.state.current_settings);
    },

    getProfiles: function() {
        this.state.client.get_profiles(function (result) {
            if (result.status >= 200 && result.status < 300) {
                this.setState({
                    errorMsg: '',
                    profiles: result.json,
                });
            } else {
                this.setState({
                    profiles: [],
                    errorMsg: result.json,
                });
            }
        }.bind(this));
    },

    getCurrentShaping: function() {
        console.log('getCurrentShaping');
        this.state.client.getCurrentShaping(function (result) {
            if (result.status == 404) {
                this.setState({
                    status: atc_status.INACTIVE,
                    errorMsg: '',
                    settings: new AtcSettings().getDefaultSettings(),
                    current_settings: new AtcSettings().getDefaultSettings(),
                });
            } else if (result.status >= 200 && result.status < 300) {
                this.setState({
                    status: atc_status.ACTIVE,
                    errorMsg: '',
                    settings: result.json,
                    current_settings: this.state.settings,
                });
            } else {
                this.setState({
                    status: atc_status.OFFLINE,
                    errorMsg: result.json,
                    settings: new AtcSettings().getDefaultSettings(),
                });
            }
        }.bind(this));
    },

    unsetShaping: function() {
        console.log('unsetShaping');
        this.state.client.unshape(function (result) {
            if (result.status >= 200 && result.status < 300) {
                this.setState({
                    status: atc_status.INACTIVE,
                    settings: new AtcSettings().getDefaultSettings(),
                    current_settings: new AtcSettings().getDefaultSettings(),
                });
            } else if (result.status >= 500) {
                this.setState({
                    status: atc_status.OFFLINE,
                    errorMsg: result.json,
                });
            }
        }.bind(this));
    },


    setShaping: function() {
        console.log('setShaping');
        this.state.client.shape(function (result) {
            if (result.status >= 200 && result.status < 300) {
                this.setState({
                    status: atc_status.ACTIVE,
                    errorMsg: '',
                    settings: result.json,
                    current_settings: {down: this.state.settings.down, up: this.state.settings.up},
                });
            } else if (result.status == 400) {
                var errors = Array();
                for (var key in result.json) {
                    errors = errors.concat(result.data[key].map(function(msg) {
                        return key + ': ' + msg;
                    }));
                }
                this.setState({
                    errorMsg: errors,
                });
            } else if (result.status >= 500) {
                this.setState({
                    status: atc_status.OFFLINE,
                    errorMsg: result.json,
                });
            }

        }.bind(this), {down: this.state.settings.down, up: this.state.settings.up});
    },

    render: function () {
        link_state = this.linkState;
        var err_msg = "";
        var update_button = false;
        if (this.state.errorMsg != "") {
            err_msg = <ErrorBox error={this.state.errorMsg} />
        }
        if (this.hasChanged()) {
            update_button = <ShapingButton id="update_button" status={atc_status.OUTDATED} onClick={this.updateClick} />
        }
        return (
            <div>
            <div className="row">
                <div id="shaping_buttons" className="col-md-12 text-center">
                    {update_button}
                    <ShapingButton id="shaping_button" status={this.state.status} onClick={this.handleClick} />
                    {err_msg}
                </div>
            </div>
            <div className="row">
                <ProfilePanel refreshProfiles={this.getProfiles} link_state={link_state} profiles={this.state.profiles} />
            </div>

            <div className="row">
                <ShapingSettings link_state={link_state} />
            </div>
            <div className="row">
                <pre className="col-md-6">{ JSON.stringify(this.state.settings) }</pre>
                <pre className="col-md-6">{ JSON.stringify(this.state.current_settings) }</pre>
            </div>
            </div>
        )
    }
});
