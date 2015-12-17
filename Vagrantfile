# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/trusty64"

  config.vm.network "forwarded_port", guest: 80, host: 8000

  config.ssh.insert_key = false

  config.vm.provision "ansible" do |ansible|
    # ansible.verbose = "v"
    ansible.playbook = "ansible/windlogger.yml"
    ansible.groups = {
      "webservers" => ["default"],
      "webserver-vagrant" => ["default"]
    }
  end



end