import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useCache } from "@/contexts/CacheContext";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faCog,
  faSave,
  faEye,
  faEyeSlash,
} from "@fortawesome/free-solid-svg-icons";

interface SettingsData {
  bot: Record<string, string | number | boolean>;
  commands: Record<string, string>;
  welcome: Record<string, string>;
  nightmode: Record<string, string>;
  tmdb: Record<string, string>;
  sonarr: Record<string, string>;
  radarr: Record<string, string>;
  web: Record<string, string | number | boolean>;
}

const CACHE_TTL = 10 * 60 * 1000; // 10 minutes

export default function Settings() {
  const cache = useCache();
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [restarting, setRestarting] = useState(false);
  const [message, setMessage] = useState("");
  const [showSecrets, setShowSecrets] = useState({
    botToken: false,
    sonarrApiKey: false,
    radarrApiKey: false,
    tmdbApiKey: false,
  });

  const toggleSecret = (field: keyof typeof showSecrets) => {
    setShowSecrets((prev) => ({
      ...prev,
      [field]: !prev[field],
    }));
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    // Check cache first
    const cachedSettings = cache.get<SettingsData>("settings");

    if (cachedSettings && !cache.isStale("settings", CACHE_TTL)) {
      setSettings(cachedSettings);
      setLoading(false);
      return;
    }

    try {
      const response = await api.get<SettingsData>("/settings/");
      setSettings(response.data);
      cache.set("settings", response.data, CACHE_TTL);
    } catch (error) {
      console.error("Failed to fetch settings:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!settings) return;

    setSaving(true);
    setMessage("");

    try {
      const response = await api.post("/settings/save", settings);
      // Update cache after successful save
      cache.set("settings", settings, CACHE_TTL);

      // Check if bot is restarting
      if (response.data.restarting) {
        setRestarting(true);
        setMessage("Settings saved! Bot is restarting...");

        // Wait for bot to restart and reload page
        setTimeout(() => {
          window.location.reload();
        }, 5000);
      } else {
        setMessage("Settings saved successfully!");
        setTimeout(() => setMessage(""), 3000);
      }
    } catch (error) {
      setMessage("Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = (
    section: keyof SettingsData,
    key: string,
    value: string | number | boolean,
  ) => {
    if (!settings) return;
    setSettings({
      ...settings,
      [section]: {
        ...settings[section],
        [key]: value,
      },
    });
  };

  if (loading || !settings) {
    return <LoadingSpinner message="Loading settings..." />;
  }

  return (
    <div className="settings-page">
      <div className="page-header flex justify-between items-center">
        <div>
          <h1>
            <FontAwesomeIcon icon={faCog} /> Settings
          </h1>
          <p className="subtitle">Configure your Telegram bot</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving || restarting}
          className="btn btn-primary"
        >
          <FontAwesomeIcon icon={faSave} />
          {restarting
            ? " Restarting..."
            : saving
              ? " Saving..."
              : " Save Settings"}
        </button>
      </div>

      {message && (
        <div
          className={`save-status ${message.includes("success") || message.includes("restarting") ? "save-status-success" : "save-status-error"}`}
        >
          {message}
        </div>
      )}

      {restarting && (
        <div
          className="card"
          style={{
            background: "var(--warning)",
            color: "#000",
            textAlign: "center",
            padding: "1rem",
          }}
        >
          <p>
            <strong>🔄 Bot is restarting...</strong>
          </p>
          <p>Page will reload automatically in a few seconds.</p>
        </div>
      )}

      {/* Bot Settings */}
      <div className="card">
        <div className="card-header">
          <h3>Bot Configuration</h3>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Bot Token</label>
              <div className="password-input-wrapper">
                <input
                  type={showSecrets.botToken ? "text" : "password"}
                  value={String(settings.bot.TOKEN || "")}
                  onChange={(e) =>
                    updateSetting("bot", "TOKEN", e.target.value)
                  }
                  className="form-control"
                />
                <button
                  type="button"
                  onClick={() => toggleSecret("botToken")}
                  className="password-toggle-btn"
                >
                  <FontAwesomeIcon
                    icon={showSecrets.botToken ? faEyeSlash : faEye}
                  />
                </button>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Timezone</label>
              <input
                type="text"
                value={String(settings.bot.TIMEZONE || "")}
                onChange={(e) =>
                  updateSetting("bot", "TIMEZONE", e.target.value)
                }
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Log Level</label>
              <select
                value={String(settings.bot.LOG_LEVEL || "INFO")}
                onChange={(e) =>
                  updateSetting("bot", "LOG_LEVEL", e.target.value)
                }
                className="form-control"
              >
                <option value="DEBUG">DEBUG</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Sonarr Settings */}
      <div className="card">
        <div className="card-header">
          <h3>Sonarr Configuration</h3>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label>Sonarr URL</label>
              <input
                type="text"
                value={settings.sonarr.URL || ""}
                onChange={(e) => updateSetting("sonarr", "URL", e.target.value)}
                className="input-field"
              />
            </div>
            <div className="form-group">
              <label>API Key</label>
              <div className="password-input-wrapper">
                <input
                  type={showSecrets.sonarrApiKey ? "text" : "password"}
                  value={settings.sonarr.API_KEY || ""}
                  onChange={(e) =>
                    updateSetting("sonarr", "API_KEY", e.target.value)
                  }
                  className="input-field"
                />
                <button
                  type="button"
                  onClick={() => toggleSecret("sonarrApiKey")}
                  className="password-toggle-btn"
                >
                  <FontAwesomeIcon
                    icon={showSecrets.sonarrApiKey ? faEyeSlash : faEye}
                  />
                </button>
              </div>
            </div>
            <div className="form-group">
              <label>Quality Profile</label>
              <input
                type="text"
                value={settings.sonarr.QUALITY_PROFILE_NAME || ""}
                onChange={(e) =>
                  updateSetting(
                    "sonarr",
                    "QUALITY_PROFILE_NAME",
                    e.target.value,
                  )
                }
                className="input-field"
              />
            </div>
            <div className="form-group">
              <label>Root Folder Path</label>
              <input
                type="text"
                value={settings.sonarr.ROOT_FOLDER_PATH || ""}
                onChange={(e) =>
                  updateSetting("sonarr", "ROOT_FOLDER_PATH", e.target.value)
                }
                className="input-field"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Radarr Settings */}
      <div className="card">
        <div className="card-header">
          <h3>Radarr Configuration</h3>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label>Radarr URL</label>
              <input
                type="text"
                value={settings.radarr.URL || ""}
                onChange={(e) => updateSetting("radarr", "URL", e.target.value)}
                className="input-field"
              />
            </div>
            <div className="form-group">
              <label>API Key</label>
              <div className="password-input-wrapper">
                <input
                  type={showSecrets.radarrApiKey ? "text" : "password"}
                  value={settings.radarr.API_KEY || ""}
                  onChange={(e) =>
                    updateSetting("radarr", "API_KEY", e.target.value)
                  }
                  className="input-field"
                />
                <button
                  type="button"
                  onClick={() => toggleSecret("radarrApiKey")}
                  className="password-toggle-btn"
                >
                  <FontAwesomeIcon
                    icon={showSecrets.radarrApiKey ? faEyeSlash : faEye}
                  />
                </button>
              </div>
            </div>
            <div className="form-group">
              <label>Quality Profile</label>
              <input
                type="text"
                value={settings.radarr.QUALITY_PROFILE_NAME || ""}
                onChange={(e) =>
                  updateSetting(
                    "radarr",
                    "QUALITY_PROFILE_NAME",
                    e.target.value,
                  )
                }
                className="input-field"
              />
            </div>
            <div className="form-group">
              <label>Root Folder Path</label>
              <input
                type="text"
                value={settings.radarr.ROOT_FOLDER_PATH || ""}
                onChange={(e) =>
                  updateSetting("radarr", "ROOT_FOLDER_PATH", e.target.value)
                }
                className="input-field"
              />
            </div>
          </div>
        </div>
      </div>

      {/* TMDB Settings */}
      <div className="card">
        <div className="card-header">
          <h3>TMDB Configuration</h3>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label>TMDB API Key</label>
              <div className="password-input-wrapper">
                <input
                  type={showSecrets.tmdbApiKey ? "text" : "password"}
                  value={settings.tmdb.API_KEY || ""}
                  onChange={(e) =>
                    updateSetting("tmdb", "API_KEY", e.target.value)
                  }
                  className="input-field"
                />
                <button
                  type="button"
                  onClick={() => toggleSecret("tmdbApiKey")}
                  className="password-toggle-btn"
                >
                  <FontAwesomeIcon
                    icon={showSecrets.tmdbApiKey ? faEyeSlash : faEye}
                  />
                </button>
              </div>
            </div>
            <div className="form-group">
              <label>Default Language</label>
              <select
                value={settings.tmdb.DEFAULT_LANGUAGE || "en"}
                onChange={(e) =>
                  updateSetting("tmdb", "DEFAULT_LANGUAGE", e.target.value)
                }
                className="input-field"
              >
                <option value="de">Deutsch (de)</option>
                <option value="en">English (en)</option>
                <option value="es">Español (es)</option>
                <option value="fr">Français (fr)</option>
                <option value="it">Italiano (it)</option>
                <option value="pt">Português (pt)</option>
                <option value="ru">Русский (ru)</option>
                <option value="ja">日本語 (ja)</option>
                <option value="ko">한국어 (ko)</option>
                <option value="zh">中文 (zh)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Night Mode Settings */}
      <div className="card">
        <div className="card-header">
          <h3>Night Mode Configuration</h3>
        </div>
        <div className="card-body">
          <div className="form-grid-nightmode">
            <div className="form-group">
              <label className="form-label">Start Time</label>
              <div className="time-input-wrapper">
                <input
                  type="time"
                  value={settings.nightmode.NIGHTMODE_START || "00:00"}
                  onChange={(e) =>
                    updateSetting(
                      "nightmode",
                      "NIGHTMODE_START",
                      e.target.value,
                    )
                  }
                  className="form-control time-input"
                />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">End Time</label>
              <div className="time-input-wrapper">
                <input
                  type="time"
                  value={settings.nightmode.NIGHTMODE_END || "08:00"}
                  onChange={(e) =>
                    updateSetting("nightmode", "NIGHTMODE_END", e.target.value)
                  }
                  className="form-control time-input"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
