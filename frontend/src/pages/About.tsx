import { useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faInfoCircle,
  faCodeBranch,
  faBox,
  faSyncAlt,
  faRobot,
  faCircle,
  faClock,
  faSignal,
  faServer,
  faUsers,
  faDesktop,
  faMicrochip,
  faMemory,
  faLifeRing,
  faBug,
  faBook,
  faHeart,
  faCode,
  faUserCircle,
  faCheckCircle,
  faExclamationCircle,
  faTimesCircle,
  faSpinner,
  faDownload,
  faPaperPlane,
} from "@fortawesome/free-solid-svg-icons";
import { faGithub, faPython, faJs } from "@fortawesome/free-brands-svg-icons";
import api from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";

interface SystemInfo {
  os: string;
  os_version: string;
  python_version: string;
  cpu_count: number;
  total_memory: number;
}

interface BotStats {
  uptime: string;
  latency: string;
  groups: number;
  members: number;
}

interface BotStatus {
  online: boolean;
}

interface AboutData {
  version: string;
  bot_status: BotStatus;
  bot_stats: BotStats;
  system_info: SystemInfo;
}

interface VersionInfo {
  local: string;
  remote: string;
  is_update_available: boolean;
  error?: string;
}

export default function About() {
  const [aboutData, setAboutData] = useState<AboutData | null>(null);
  const [versionInfo, setVersionInfo] = useState<VersionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [checking, setChecking] = useState(false);

  const fetchAboutData = async () => {
    try {
      const response = await api.get("/about/data");
      setAboutData(response.data);
    } catch (error) {
      console.error("Error fetching about data:", error);
    }
  };

  const checkVersion = async () => {
    setChecking(true);
    try {
      const response = await api.get("/about/version");
      setVersionInfo(response.data);
    } catch (error) {
      console.error("Error checking version:", error);
      setVersionInfo({
        local: "unknown",
        remote: "unknown",
        is_update_available: false,
        error: "Error checking for updates",
      });
    } finally {
      setChecking(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchAboutData(), checkVersion()]);
      setLoading(false);
    };
    loadData();
  }, []);

  const handleRefresh = () => {
    checkVersion();
  };

  if (loading || !aboutData) {
    return <LoadingSpinner message="Loading about information..." />;
  }

  const renderUpdateStatus = () => {
    if (checking) {
      return (
        <div className="update-status checking">
          <FontAwesomeIcon icon={faSpinner} spin /> Checking for updates...
        </div>
      );
    }

    if (!versionInfo) {
      return null;
    }

    if (versionInfo.error) {
      return (
        <div className="update-status error">
          <FontAwesomeIcon icon={faTimesCircle} /> {versionInfo.error}
        </div>
      );
    }

    if (versionInfo.is_update_available) {
      return (
        <div className="update-status update-available">
          <div className="update-content">
            <div>
              <FontAwesomeIcon icon={faExclamationCircle} />
              <strong> Update Available!</strong> v{versionInfo.remote} is
              available
            </div>
            <a
              href="https://github.com/cyb3rgh05t/telegram-bot/releases/latest"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-sm btn-warning"
            >
              <FontAwesomeIcon icon={faDownload} /> Update Now
            </a>
          </div>
        </div>
      );
    }

    return (
      <div className="update-status up-to-date">
        <FontAwesomeIcon icon={faCheckCircle} /> You are running the latest
        version
      </div>
    );
  };

  return (
    <div className="about-page">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faInfoCircle} /> About Telegram Bot
        </h1>
        <p className="subtitle">
          Version information, system details, and support
        </p>
      </div>

      {/* Version Information Card */}
      <div className="card-grid">
        <div className="card about-card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faCodeBranch} /> Version Information
            </h3>
            <button
              className="btn btn-sm btn-primary"
              onClick={handleRefresh}
              disabled={checking}
            >
              <FontAwesomeIcon icon={faSyncAlt} spin={checking} />
            </button>
          </div>
          <div className="card-body">
            <div className="version-display">
              <div className="version-icon">
                <FontAwesomeIcon icon={faBox} />
              </div>
              <div className="version-details">
                <h4>Current Version</h4>
                <p className="version-number">v{aboutData.version}</p>
              </div>
            </div>

            {renderUpdateStatus()}

            <div className="version-actions">
              <a
                href="https://github.com/cyb3rgh05t/telegram-bot/releases"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline"
              >
                <FontAwesomeIcon icon={faGithub} /> View Releases
              </a>
              <a
                href="https://github.com/cyb3rgh05t/telegram-bot/releases/latest"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary"
              >
                <FontAwesomeIcon icon={faDownload} /> Latest Release
              </a>
            </div>
          </div>
        </div>

        {/* Bot Status Card */}
        <div className="card about-card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faRobot} /> Bot Status
            </h3>
          </div>
          <div className="card-body">
            <div className="status-display">
              <div
                className={`status-icon ${
                  aboutData.bot_status.online ? "online" : "offline"
                }`}
              >
                <FontAwesomeIcon icon={faCircle} />
              </div>
              <div className="status-details">
                <h4>{aboutData.bot_status.online ? "Online" : "Offline"}</h4>
                <p>
                  Bot is currently{" "}
                  {aboutData.bot_status.online ? "running" : "not running"}
                </p>
              </div>
            </div>

            <div className="stats-grid">
              <div className="stat-box">
                <FontAwesomeIcon icon={faClock} />
                <div>
                  <span className="stat-label">Uptime</span>
                  <span className="stat-value">
                    {aboutData.bot_stats.uptime}
                  </span>
                </div>
              </div>
              <div className="stat-box">
                <FontAwesomeIcon icon={faSignal} />
                <div>
                  <span className="stat-label">Latency</span>
                  <span className="stat-value">
                    {aboutData.bot_stats.latency}
                  </span>
                </div>
              </div>
              <div className="stat-box">
                <FontAwesomeIcon icon={faPaperPlane} />
                <div>
                  <span className="stat-label">Groups</span>
                  <span className="stat-value">
                    {aboutData.bot_stats.groups}
                  </span>
                </div>
              </div>
              <div className="stat-box">
                <FontAwesomeIcon icon={faUsers} />
                <div>
                  <span className="stat-label">Members</span>
                  <span className="stat-value">
                    {aboutData.bot_stats.members}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* System Information & Support */}
      <div className="card-grid">
        <div className="card about-card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faServer} /> System Information
            </h3>
          </div>
          <div className="card-body">
            <div className="info-list">
              <div className="info-item">
                <FontAwesomeIcon icon={faDesktop} />
                <span className="info-label">Operating System</span>
                <span className="info-value">
                  {aboutData.system_info.os} {aboutData.system_info.os_version}
                </span>
              </div>
              <div className="info-item">
                <FontAwesomeIcon icon={faPython} />
                <span className="info-label">Python Version</span>
                <span className="info-value">
                  {aboutData.system_info.python_version}
                </span>
              </div>
              <div className="info-item">
                <FontAwesomeIcon icon={faMicrochip} />
                <span className="info-label">CPU Cores</span>
                <span className="info-value">
                  {aboutData.system_info.cpu_count}
                </span>
              </div>
              <div className="info-item">
                <FontAwesomeIcon icon={faMemory} />
                <span className="info-label">Total Memory</span>
                <span className="info-value">
                  {aboutData.system_info.total_memory} GB
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Support & Links Card */}
        <div className="card about-card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faLifeRing} /> Support & Links
            </h3>
          </div>
          <div className="card-body">
            <div className="links-grid">
              <a
                href="https://github.com/cyb3rgh05t/telegram-bot"
                target="_blank"
                rel="noopener noreferrer"
                className="link-card"
              >
                <FontAwesomeIcon icon={faGithub} />
                <div>
                  <h5>GitHub Repository</h5>
                  <p>View source code</p>
                </div>
              </a>
              <a
                href="https://github.com/cyb3rgh05t/telegram-bot/issues"
                target="_blank"
                rel="noopener noreferrer"
                className="link-card"
              >
                <FontAwesomeIcon icon={faBug} />
                <div>
                  <h5>Report Issues</h5>
                  <p>Submit bug reports</p>
                </div>
              </a>
              <a
                href="https://github.com/cyb3rgh05t/telegram-bot/wiki"
                target="_blank"
                rel="noopener noreferrer"
                className="link-card"
              >
                <FontAwesomeIcon icon={faBook} />
                <div>
                  <h5>Documentation</h5>
                  <p>Read the docs</p>
                </div>
              </a>
              <a
                href="https://ko-fi.com/cyb3rgh05t"
                target="_blank"
                rel="noopener noreferrer"
                className="link-card kofi"
              >
                <FontAwesomeIcon icon={faHeart} />
                <div>
                  <h5>Support on Ko-fi</h5>
                  <p>Buy me a coffee</p>
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Credits Card */}
      <div className="card about-card credits-card">
        <div className="card-header">
          <h3>
            <FontAwesomeIcon icon={faCode} /> Credits & Technologies
          </h3>
        </div>
        <div className="card-body">
          <div className="credits-grid">
            <div className="credit-section">
              <h4>
                <FontAwesomeIcon icon={faGithub} /> Developer
              </h4>
              <a
                href="https://github.com/cyb3rgh05t"
                target="_blank"
                rel="noopener noreferrer"
                className="developer-link"
              >
                <FontAwesomeIcon icon={faUserCircle} /> cyb3rgh05t
              </a>
            </div>
            <div className="credit-section">
              <h4>
                <FontAwesomeIcon icon={faCode} /> Technologies
              </h4>
              <div className="tech-tags">
                <span className="tech-tag">
                  <FontAwesomeIcon icon={faPython} /> Python
                </span>
                <span className="tech-tag">
                  <FontAwesomeIcon icon={faServer} /> FastAPI
                </span>
                <span className="tech-tag">
                  <FontAwesomeIcon icon={faJs} /> React
                </span>
                <span className="tech-tag">
                  <FontAwesomeIcon icon={faServer} /> SQLite
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
