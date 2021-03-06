package pasalab.dfs.perf.basic;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.apache.log4j.Logger;

import pasalab.dfs.perf.conf.PerfConf;
import pasalab.dfs.perf.util.SAXConfiguration;

/**
 * Manage the configurations for each task.
 */
public class TaskConfiguration {
  private static final Logger LOG = Logger.getLogger("");
  public static final boolean DEFAULT_BOOLEAN = false;
  public static final int DEFAULT_INTEGER = 0;
  public static final long DEFAULT_LONG = 0;
  public static final String DEFAULT_STRING = "";

  private static TaskConfiguration sTaskConf = null;

  /**
   * Get the configuration.
   * 
   * @param type the type of the benchmark task
   * @param fromFile if true, it will load the configuration file, otherwise it return an empty
   *        configuration.
   * @return the task configuration
   */
  public static synchronized TaskConfiguration get(String type, boolean fromFile) {
    if (sTaskConf == null) {
      if (fromFile) {
        try {
          sTaskConf =
              new TaskConfiguration(PerfConf.get().DFS_PERF_HOME + "/conf/testsuite/" + type
                  + ".xml");
        } catch (Exception e) {
          LOG.error("Error when parse conf/testsuite/" + type + ".xml", e);
          throw new RuntimeException("Failed to parse conf/testsuite/" + type + ".xml");
        }
      } else {
        sTaskConf = new TaskConfiguration();
      }
    }
    return sTaskConf;
  }

  private Map<String, String> mProperties;

  private TaskConfiguration() {
    mProperties = new HashMap<String, String>();
  }

  private TaskConfiguration(String xmlFileName) throws Exception {
    SAXParserFactory spf = SAXParserFactory.newInstance();
    SAXParser saxParser = spf.newSAXParser();
    File xmlFile = new File(xmlFileName);
    SAXConfiguration saxConfiguration = new SAXConfiguration();
    saxParser.parse(xmlFile, saxConfiguration);
    mProperties = saxConfiguration.getProperties();
  }

  public synchronized void addProperty(String name, String value) {
    mProperties.put(name, value);
  }

  public synchronized Map<String, String> getAllProperties() {
    Map<String, String> ret = new HashMap<String, String>(mProperties.size());
    ret.putAll(mProperties);
    return ret;
  }

  public synchronized boolean getBooleanProperty(String property) {
    if (mProperties.containsKey(property)) {
      return Boolean.valueOf(mProperties.get(property));
    }
    return DEFAULT_BOOLEAN;
  }

  public synchronized int getIntProperty(String property) {
    if (mProperties.containsKey(property)) {
      return Integer.valueOf(mProperties.get(property));
    }
    return DEFAULT_INTEGER;
  }

  public synchronized long getLongProperty(String property) {
    if (mProperties.containsKey(property)) {
      return Long.valueOf(mProperties.get(property));
    }
    return DEFAULT_LONG;
  }

  public synchronized String getProperty(String property) {
    if (mProperties.containsKey(property)) {
      return mProperties.get(property);
    }
    return DEFAULT_STRING;
  }

  public synchronized boolean hasProperty(String property) {
    return mProperties.containsKey(property);
  }
}
