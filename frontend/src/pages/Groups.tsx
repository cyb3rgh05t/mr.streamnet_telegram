import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useCache } from "@/contexts/CacheContext";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faUsers,
  faMoon,
  faLanguage,
  faUserShield,
  faChartBar,
} from "@fortawesome/free-solid-svg-icons";

interface GroupStats {
  member_count: number;
  admin_count: number;
  created_at?: string;
  last_activity?: string;
}

interface GroupItem {
  id: number;
  group_chat_id: number;
  group_name?: string;
  language?: string;
  night_mode_active: boolean;
  stats?: GroupStats;
}

const CACHE_TTL = 2 * 60 * 1000; // 2 minutes

export default function Groups() {
  const cache = useCache();
  const [groups, setGroups] = useState<GroupItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    // Check cache first
    const cachedGroups = cache.get<GroupItem[]>("groups");

    if (cachedGroups && !cache.isStale("groups", CACHE_TTL)) {
      setGroups(cachedGroups);
      setLoading(false);
      return;
    }

    try {
      const response = await api.get("/groups/");
      const groupsData = response.data.groups;
      setGroups(groupsData);
      cache.set("groups", groupsData, CACHE_TTL);
    } catch (error) {
      console.error("Failed to fetch groups:", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleNightMode = async (group: GroupItem) => {
    try {
      await api.post("/groups/update", {
        group_chat_id: group.group_chat_id,
        field: "night_mode_active",
        value: !group.night_mode_active,
      });

      const updatedGroups = groups.map((g) =>
        g.id === group.id
          ? { ...g, night_mode_active: !g.night_mode_active }
          : g,
      );

      setGroups(updatedGroups);
      // Update cache with new data
      cache.set("groups", updatedGroups, CACHE_TTL);
    } catch (error) {
      console.error("Failed to update group:", error);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading groups..." />;
  }

  return (
    <div className="groups-page">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faUsers} /> Groups
        </h1>
        <p className="subtitle">Manage your Telegram groups</p>
      </div>

      <div className="card">
        <div className="card-body">
          {groups.length === 0 ? (
            <div className="empty-state">
              <FontAwesomeIcon icon={faUsers} className="text-6xl mb-4" />
              <h3>No groups configured yet</h3>
              <p>Add the bot to a group and use /set_group_id to register it</p>
            </div>
          ) : (
            <div className="groups-list">
              {groups.map((group) => (
                <div key={group.id} className="group-card">
                  <div className="group-header">
                    <div className="group-info">
                      <h3 className="group-name">
                        {group.group_name || `Group ${group.group_chat_id}`}
                      </h3>
                      <p className="group-id">ID: {group.group_chat_id}</p>
                    </div>
                    <button
                      onClick={() => toggleNightMode(group)}
                      className={`btn btn-sm ${
                        group.night_mode_active ? "btn-warning" : "btn-outline"
                      }`}
                    >
                      <FontAwesomeIcon icon={faMoon} />
                      {group.night_mode_active ? "ON" : "OFF"}
                    </button>
                  </div>

                  {/* Statistics */}
                  {group.stats && (
                    <div className="group-stats">
                      <div className="stat-item">
                        <FontAwesomeIcon icon={faUsers} className="stat-icon" />
                        <div className="stat-content">
                          <span className="stat-label">Members</span>
                          <span className="stat-value">
                            {group.stats.member_count}
                          </span>
                        </div>
                      </div>
                      <div className="stat-item">
                        <FontAwesomeIcon
                          icon={faUserShield}
                          className="stat-icon"
                        />
                        <div className="stat-content">
                          <span className="stat-label">Admins</span>
                          <span className="stat-value">
                            {group.stats.admin_count}
                          </span>
                        </div>
                      </div>
                      <div className="stat-item">
                        <FontAwesomeIcon
                          icon={faLanguage}
                          className="stat-icon"
                        />
                        <div className="stat-content">
                          <span className="stat-label">Language</span>
                          <span className="stat-value">
                            {group.language || "en"}
                          </span>
                        </div>
                      </div>
                      <div className="stat-item">
                        <FontAwesomeIcon
                          icon={faChartBar}
                          className="stat-icon"
                        />
                        <div className="stat-content">
                          <span className="stat-label">Status</span>
                          <span
                            className={`stat-value ${
                              group.night_mode_active
                                ? "text-warning"
                                : "text-success"
                            }`}
                          >
                            {group.night_mode_active ? "Paused" : "Active"}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
