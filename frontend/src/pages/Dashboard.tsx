import { useEffect, useState } from "react";
import api from "@/lib/api";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faTachometerAlt,
  faPaperPlane,
  faUsers,
  faFilm,
  faTv,
  faMicrochip,
  faMemory,
  faHdd,
  faCheckCircle,
  faServer,
  faClock,
} from "@fortawesome/free-solid-svg-icons";

interface BotStatus {
  online: boolean;
  name: string;
  uptime: string;
  groups: number;
  users: number;
  latency?: number;
}

interface MediaStats {
  sonarr_total: number;
  radarr_total: number;
  pending_requests: number;
}

interface GroupStats {
  total: number;
  night_mode_enabled: number;
}

interface ResourceItem {
  percent: number;
  label: string;
}

interface SystemResources {
  cpu: ResourceItem;
  memory: ResourceItem;
  disk: ResourceItem;
}

interface ServiceItem {
  name: string;
  status: string;
  icon: string;
}

interface DashboardData {
  bot_status: BotStatus;
  media_stats: MediaStats;
  group_stats: GroupStats;
  resources: SystemResources;
  services: ServiceItem[];
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get<DashboardData>("/dashboard/");
      setData(response.data);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return <LoadingSpinner message="Loading dashboard..." />;
  }

  const getResourceClass = (percent: number) => {
    if (percent > 80) return "danger";
    if (percent > 60) return "warning";
    return "success";
  };

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faTachometerAlt} /> Dashboard
        </h1>
        <p className="subtitle">Overview of your Telegram bot</p>
      </div>

      {/* Bot Status Banner */}
      <div className="status-banner-modern">
        <div className="bot-name-section">
          <span
            className={`status-dot ${
              data.bot_status.online ? "online" : "offline"
            }`}
          ></span>
          <h2 className="bot-name">{data.bot_status.name}</h2>
        </div>
        <div className="bot-stats-grid">
          <div className="bot-stat-box">
            <FontAwesomeIcon icon={faClock} className="stat-icon-small" />
            <div className="stat-content">
              <span className="stat-label-small">Uptime</span>
              <span className="stat-value-small">{data.bot_status.uptime}</span>
            </div>
          </div>
          <div className="bot-stat-box">
            <FontAwesomeIcon icon={faPaperPlane} className="stat-icon-small" />
            <div className="stat-content">
              <span className="stat-label-small">Latency</span>
              <span className="stat-value-small">
                {data.bot_status.latency
                  ? `${data.bot_status.latency.toFixed(2)}ms`
                  : "N/A"}
              </span>
            </div>
          </div>
          <div className="bot-stat-box">
            <FontAwesomeIcon icon={faUsers} className="stat-icon-small" />
            <div className="stat-content">
              <span className="stat-label-small">Guilds</span>
              <span className="stat-value-small">{data.bot_status.groups}</span>
            </div>
          </div>
          <div className="bot-stat-box">
            <FontAwesomeIcon icon={faUsers} className="stat-icon-small" />
            <div className="stat-content">
              <span className="stat-label-small">Members</span>
              <span className="stat-value-small">{data.bot_status.users}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="quick-stats">
        <div className="stat-card">
          <div className="stat-icon groups-icon">
            <FontAwesomeIcon icon={faUsers} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data.group_stats.total}</div>
            <div className="stat-label">Total Groups</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon media-icon">
            <FontAwesomeIcon icon={faFilm} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data.media_stats.sonarr_total}</div>
            <div className="stat-label">Sonarr Series</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon media-icon">
            <FontAwesomeIcon icon={faTv} />
          </div>
          <div className="stat-info">
            <div className="stat-value">{data.media_stats.radarr_total}</div>
            <div className="stat-label">Radarr Movies</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon services-icon">
            <FontAwesomeIcon icon={faCheckCircle} />
          </div>
          <div className="stat-info">
            <div className="stat-value">
              {data.services.filter((s) => s.status === "running").length}/
              {data.services.length}
            </div>
            <div className="stat-label">Services Running</div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="dashboard-grid">
        {/* System Resources */}
        <div className="card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faMicrochip} /> System Resources
            </h3>
          </div>
          <div className="card-body">
            <div className="resource-bars">
              <div className="resource-item">
                <div className="resource-header">
                  <span className="resource-label">
                    <FontAwesomeIcon icon={faMicrochip} /> CPU
                  </span>
                  <span className="resource-value">
                    {data.resources.cpu.percent.toFixed(1)}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div
                    className={`progress-fill ${getResourceClass(
                      data.resources.cpu.percent,
                    )}`}
                    style={{ width: `${data.resources.cpu.percent}%` }}
                  ></div>
                </div>
              </div>

              <div className="resource-item">
                <div className="resource-header">
                  <span className="resource-label">
                    <FontAwesomeIcon icon={faMemory} /> Memory
                  </span>
                  <span className="resource-value">
                    {data.resources.memory.percent.toFixed(1)}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div
                    className={`progress-fill ${getResourceClass(
                      data.resources.memory.percent,
                    )}`}
                    style={{ width: `${data.resources.memory.percent}%` }}
                  ></div>
                </div>
              </div>

              <div className="resource-item">
                <div className="resource-header">
                  <span className="resource-label">
                    <FontAwesomeIcon icon={faHdd} /> Disk
                  </span>
                  <span className="resource-value">
                    {data.resources.disk.percent.toFixed(1)}%
                  </span>
                </div>
                <div className="progress-bar">
                  <div
                    className={`progress-fill ${getResourceClass(
                      data.resources.disk.percent,
                    )}`}
                    style={{ width: `${data.resources.disk.percent}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Services Status */}
        <div className="card">
          <div className="card-header">
            <h3>
              <FontAwesomeIcon icon={faServer} /> Services
            </h3>
          </div>
          <div className="card-body">
            <div className="services-list">
              {data.services.map((service, index) => (
                <div key={index} className="service-item">
                  <div className="service-name">
                    <FontAwesomeIcon icon={faPaperPlane} />
                    {service.name}
                  </div>
                  <div className={`service-status ${service.status}`}>
                    <span className="status-dot"></span>
                    {service.status.charAt(0).toUpperCase() +
                      service.status.slice(1)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
