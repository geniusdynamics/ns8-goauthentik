# Authentik for NethServer 8

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Authentik Version](https://img.shields.io/badge/Authentik-2025.8.0-blue)](https://goauthentik.io/)

A comprehensive NethServer 8 module that integrates **Authentik**, the open-source Identity Provider, into your NethServer infrastructure. Authentik provides centralized authentication, authorization, and user management with support for OAuth2, SAML, LDAP, and many other protocols.

## ✨ Features

- **Centralized Identity Management**: Single sign-on (SSO) across all your applications
- **Multi-Protocol Support**: OAuth2, OpenID Connect, SAML, LDAP, SCIM, and more
- **User-Friendly Interface**: Modern Vue.js-based management interface
- **Enterprise-Ready**: Built for production environments with high availability
- **Extensible**: Support for custom flows, policies, and integrations
- **Secure**: Built-in security features including MFA, password policies, and audit logging

## 🚀 Quick Start

### Prerequisites

- NethServer 8 installed and running
- Administrative access to the NethServer cluster
- A domain name for the Authentik instance

### Installation

1. **Add the module to your NethServer cluster:**

   ```bash
   add-module ghcr.io/geniusdynamics/goauthentik:latest 1
   ```

   The command will return output similar to:
   ```json
   {"module_id": "goauthentik1", "image_name": "goauthentik", "image_url": "ghcr.io/geniusdynamics/goauthentik:latest"}
   ```

2. **Configure the module:**

   ```bash
   api-cli run configure-module --agent module/goauthentik1 --data - <<EOF
   {
     "host": "auth.yourdomain.com",
     "http2https": true,
     "lets_encrypt": true
   }
   EOF
   ```

3. **Complete the initial setup:**

   - Open your browser and navigate to `https://auth.yourdomain.com/if/flow/initial-setup/`
   - Follow the on-screen instructions to complete the Authentik setup
   - Configure your first authentication flow and create administrative users

## ⚙️ Configuration

### Configuration Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `host` | string | Yes | Fully qualified domain name for the Authentik instance |
| `http2https` | boolean | Yes | Enable HTTP to HTTPS redirection |
| `lets_encrypt` | boolean | Yes | Enable Let's Encrypt SSL certificate |

### Example Configuration

```bash
api-cli run configure-module --agent module/goauthentik1 --data '{
  "host": "auth.company.com",
  "http2https": true,
  "lets_encrypt": true
}'
```

### Getting Current Configuration

```bash
api-cli run get-configuration --agent module/goauthentik1
```

## 🔧 Management Commands

### Update Module

To update to the latest version:

```bash
api-cli run update-module --data '{
  "module_url": "ghcr.io/geniusdynamics/goauthentik:latest",
  "instances": ["goauthentik1"],
  "force": true
}'
```

### Uninstall Module

To remove the Authentik instance:

```bash
remove-module --no-preserve goauthentik1
```

## 🏗️ Architecture

This module is built using modern containerized architecture:

- **Frontend**: Vue.js 2.x with Carbon Design System
- **Backend**: Authentik server with PostgreSQL and Redis
- **Containerization**: Podman with rootless containers
- **Reverse Proxy**: Traefik integration for SSL termination
- **Service Management**: Systemd user services

### Container Structure

- **Authentik Server**: Main application container
- **PostgreSQL**: Database backend
- **Redis**: Caching and session storage
- **Nginx**: Web server for static assets

## 🧪 Testing

The module includes comprehensive test suites using Robot Framework:

```bash
./test-module.sh <NODE_ADDR> ghcr.io/geniusdynamics/goauthentik:latest
```

Tests cover:
- Module installation and configuration
- Service availability and functionality
- Integration with NethServer core services
- SSL certificate management

## 🔍 Debugging

### Environment Variables

Check module environment variables:

```bash
runagent -m goauthentik1 env
```

### Container Inspection

List running containers:

```bash
runagent -m goauthentik1 podman ps
```

Access container shell:

```bash
runagent -m goauthentik1 podman exec -ti goauthentik-app sh
```

### Service Logs

View service logs:

```bash
runagent -m goauthentik1 journalctl --user -u goauthentik.service
```

## 🌐 Internationalization

The UI supports multiple languages and is translated using [Weblate](https://hosted.weblate.org/projects/ns8/):

- English (en)
- Spanish (es)
- Italian (it)
- German (de)
- Portuguese (pt, pt_BR)
- European Basque (eu)

### Adding Translations

1. Add the [GitHub Weblate app](https://docs.weblate.org/en/latest/admin/continuous.html#github-setup) to your repository
2. Add your repository to [hosted.weblate.org](https://hosted.weblate.org) or request addition to the ns8 Weblate project

## 🛠️ Development

### Project Structure

```
├── imageroot/              # Module configuration and scripts
│   ├── actions/           # Module actions (configure, install, etc.)
│   ├── systemd/           # Service definitions
│   └── events/            # Event handlers
├── ui/                    # Vue.js frontend application
│   ├── src/              # Source code
│   ├── public/           # Static assets
│   └── dist/             # Built assets
├── tests/                # Robot Framework tests
├── build-images.sh       # Build script
└── README.md            # This file
```

### Building from Source

1. **Build the UI:**

   ```bash
   cd ui
   yarn install
   yarn build
   ```

2. **Build the container image:**

   ```bash
   ./build-images.sh
   ```

3. **Push to registry:**

   ```bash
   buildah push ghcr.io/geniusdynamics/goauthentik:latest
   ```

### Development Environment

Set up a development environment:

```bash
# Clone the repository
git clone https://github.com/geniusdynamics/ns8-goauthentik.git
cd ns8-goauthentik

# Install UI dependencies
cd ui
yarn install

# Start development server
yarn serve
```

## 📚 Documentation

- [Authentik Documentation](https://docs.goauthentik.io/)
- [NethServer 8 Documentation](https://nethserver.github.io/ns8-core/)
- [Community Forum Thread](https://community.nethserver.org/t/authentik-sso-app-for-nethserver-8/22873/105)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code style and conventions
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting PRs

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Kemboi Elvis** - *Lead Developer* - [kemboielvis@genius.ke](mailto:kemboielvis@genius.ke)
- **Martin Bhuong** - *Contributor* - [martin@genius.ke](mailto:martin@genius.ke)

## 🙏 Acknowledgments

- [Authentik Project](https://goauthentik.io/) for the excellent identity management platform
- [NethServer Community](https://community.nethserver.org/) for the robust server platform
- [Genius Dynamics](https://genius.ke) for sponsoring this module development

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/geniusdynamics/ns8-goauthentik/issues)
- **Documentation**: [Authentik Docs](https://docs.goauthentik.io/)
- **Community**: [NethServer Community Forum](https://community.nethserver.org/)

---

**Made with ❤️ by the Genius Dynamics Team**
