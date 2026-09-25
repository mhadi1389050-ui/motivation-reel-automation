import json
import sys
from agents.agent_1_topic_research import TopicResearchAgent
from utils.helpers import load_config, save_output

def main():
    print("🎬 Motivation Reel Automation Pipeline")
    print("=" * 50)
    
    # Load config
    config = load_config("config/api_keys_template.json")
    settings = load_config("config/settings.json")
    
    print("✅ Configuration loaded")
    
    # Agent 1: Topic Research
    print("\n🔍 Starting Agent 1: Topic Research...")
    agent_1 = TopicResearchAgent(config, settings)
    agent_1_output = agent_1.run()
    
    # Save output
    save_output(agent_1_output, "outputs/agent_1_output.json")
    
    print("✅ Pipeline completed!")
    print(f"\n📌 Selected Topic: {agent_1_output['topic']}")
    print(f"📈 Viral Probability: {agent_1_output['viral_probability']}")

if __name__ == "__main__":
    main()
