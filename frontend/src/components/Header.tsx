import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="bg-white border-b border-border sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-xl font-bold text-education-blue">
              教育科技
            </h1>
            <nav className="hidden md:flex items-center space-x-6">
              <Link to="/chat" className="text-foreground hover:text-education-blue transition-colors">
                AI助手
              </Link>
              <a href="#profile" className="text-foreground hover:text-education-blue transition-colors">
                个人中心
              </a>
            </nav>
          </div>
          <Button variant="default" className="bg-education-gradient text-white hover:opacity-90">
            登录/注册
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Header;