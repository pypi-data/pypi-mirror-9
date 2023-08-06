#
#    NEPI, a framework to manage network experiments
#    Copyright (C) 2013 INRIA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation;
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Alina Quereilhac <alina.quereilhac@inria.fr>

# TODO: Investigate using http://nixos.org/nix/

def install_packages_command(os, packages):
    if not isinstance(packages, list):
        packages = [packages]

    cmd = " && ".join(map(lambda p: 
            " { dpkg -s %(package)s || sudo -S apt-get -y install %(package)s ; } " % {
                    'package': p}, packages))
        
    #cmd = { dpkg -s vim || sudo -S apt-get -y install vim ; } && ..
    return cmd 

def remove_packages_command(os, packages):
    if not isinstance(packages, list):
        packages = [packages]

    cmd = " && ".join(map(lambda p: 
            " { dpkg -s %(package)s && sudo -S apt-get -y purge %(package)s ; } " % {
                    'package': p}, packages))
        
    #cmd = { dpkg -s vim && sudo -S apt-get -y purge vim ; } && ..
    return cmd 

