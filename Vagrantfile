Vagrant.configure("2") do |config|
  config.vm.box = "debian/jessie64"
  config.vm.hostname = "qa-arilo-box"

  config.vm.provision :shell, path: "bootstrap.sh"

  config.vm.network :private_network, ip: "192.168.255.39"

  config.ssh.forward_agent = true

  config.vm.synced_folder "../www2", "/srv/www", :nfs => true
  config.vm.synced_folder "../dbs2", "/srv/dbs", :nfs => true
  config.vm.synced_folder "./docker", "/docker", :nfs => true
  config.vm.synced_folder "./deploy", "/deploy", :nfs => true

  config.vm.provider :virtualbox do |vb|
    vb.name = "QA Arilo Box 1.0"
    vb.customize [
      "modifyvm", :id,
      "--memory", 8192,
      "--cpus", 2
    ]
  end  
end
