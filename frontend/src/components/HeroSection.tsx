import { Button } from "@/components/ui/button";
import { ChevronDown } from "lucide-react";
import educationDashboard from "@/assets/education-dashboard.jpg";

const HeroSection = () => {
  return (
    <section className="bg-hero-gradient min-h-screen flex items-center">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="space-y-4">
              <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
                <span className="text-education-blue">AI智能</span>{" "}
                <span className="text-foreground">教育</span>
              </h1>
              <p className="text-lg text-muted-foreground leading-relaxed max-w-lg">
                教育帮助家庭为孩子制定课程，
                完美融合中西方教育体系优势。
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-4">
              <Button size="lg" className="bg-education-gradient text-white hover:opacity-90">
                开始您的教育路径
              </Button>
              <Button variant="outline" size="lg" className="border-education-blue text-education-blue hover:bg-education-light-blue">
                了解更多
              </Button>
            </div>
          </div>
          <div className="relative">
            <div className="bg-white rounded-lg shadow-2xl p-1">
              <img 
                src={educationDashboard} 
                alt="教育规划仪表板" 
                className="w-full h-auto rounded-lg"
              />
            </div>
            <div className="absolute -top-4 -right-4 w-8 h-8 bg-education-blue rounded-full"></div>
            <div className="absolute -bottom-4 -left-4 w-6 h-6 bg-accent rounded-full"></div>
            <div className="absolute top-1/2 -left-6 w-4 h-4 bg-yellow-400 rounded-full"></div>
          </div>
        </div>
        
        <div className="text-center mt-16">
          <p className="text-muted-foreground mb-4">向下滚动了解更多</p>
          <ChevronDown className="w-6 h-6 text-education-blue mx-auto animate-bounce" />
        </div>
      </div>
    </section>
  );
};

export default HeroSection;