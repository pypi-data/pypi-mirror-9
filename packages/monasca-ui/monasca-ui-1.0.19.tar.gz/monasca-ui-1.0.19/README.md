monasca-ui
==========

Monasca UI is implemented as a horizon plugin that adds panels to horizon. It is installed into devstack
by monasca-vagrant. For a UI development setup:
* git clone https://github.com/openstack/horizon.git  # clone horizon
* git clone https://github.com/hpcloud-mon/grafana.git
* ln -s grafana/src horizon/static/grafana

* cd horizon
* Add git+https://github.com/stackforge/monasca-ui.git  to requirements.txt
* Edit openstack_dashboard/settings.py to include the following two lines:
* import monitoring.enabled
* monitoring.enabled, #Add to the settings.update_dashboards list
# 
License

Copyright (c) 2014 Hewlett-Packard Development Company, L.P.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
    
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied.
See the License for the specific language governing permissions and
limitations under the License.

