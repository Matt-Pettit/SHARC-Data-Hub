#!/bin/bash

# Function to install common dependencies
install_common_dependencies() {
    sudo apt update
    sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
    sudo apt update
    sudo apt install -y caddy python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
}

# Function to install Flask and required libraries
install_flask_libraries_server() {
    sudo pip3 install Flask kml2geojson pandas SQLAlchemy Werkzeug gunicorn
}

install_flask_libraries_mobile() {
    sudo apt install python3-flask
    sudo apt install python3-flask-session
    sudo apt install python3-pandas
    sudo apt install python3-sqlalchemy
    sudo apt install python3-werkzeug
    sudo apt install python3-gunicorn
    sudo pip3 install kml2geojson --break-system-packages
}

# Function to configure Caddy for mobile deployment
configure_caddy_mobile() {
    echo "
    :80 {
        reverse_proxy 127.0.0.1:8000
    }
    " | sudo tee /etc/caddy/Caddyfile
}

# Function to configure Caddy for server deployment
configure_caddy_server() {
    local domain=$1
    echo "
    www.$domain {
        redir https://$domain{uri}
    }

    $domain {
        reverse_proxy localhost:8000
    }
    " | sudo tee /etc/caddy/Caddyfile
}

# Function to generate run script
generate_run_script() {
    local workers=$1
    echo "#!/bin/bash
    gunicorn --workers $workers --bind 127.0.0.1:8000 App:application" > run.sh
    chmod +x run.sh
}

# Main script
echo "Flask Deployment Script"
echo "1. Mobile Deployment (Raspberry Pi)"
echo "2. Server Deployment (VPS/Server)"
read -p "Select deployment type (1/2): " deployment_type

install_common_dependencies


if [ "$deployment_type" == "1" ]; then
    install_flask_libraries_mobile
    configure_caddy_mobile
    echo "Mobile deployment configured."
elif [ "$deployment_type" == "2" ]; then
    install_flask_libraries_server
    read -p "Enter your domain name (e.g., example.com): " domain_name
    configure_caddy_server $domain_name
    echo "Server deployment configured for $domain_name"
else
    echo "Invalid selection. Exiting."
    exit 1
fi


sudo systemctl reload caddy
read -p "Enter the number of Gunicorn workers: " num_workers
generate_run_script $num_workers

echo "Deployment script completed. Use './run.sh' to start your application."