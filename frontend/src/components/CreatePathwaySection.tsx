import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChevronLeft, ChevronRight } from "lucide-react";

const CreatePathwaySection = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    childName: "",
    childAge: "",
    gender: "",
    location: ""
  });

  const steps = [
    { id: 1, title: "基本信息", active: true },
    { id: 2, title: "教育背景", active: false },
    { id: 3, title: "目标规划", active: false }
  ];

  const handleNext = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <section id="create" className="py-20 bg-white">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold mb-4">
            创建 <span className="text-education-blue">您孩子的教育路径</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            填写您孩子的一些关键信息，以生成个性化的
            教育路径和差距分析。
          </p>
        </div>

        <Card className="shadow-xl border-0">
          <CardHeader className="bg-education-light-blue">
            <div className="flex justify-center space-x-8">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full text-sm font-semibold ${
                    currentStep >= step.id 
                      ? 'bg-education-blue text-white' 
                      : 'bg-gray-200 text-gray-500'
                  }`}>
                    {step.id}
                  </div>
                  <span className={`ml-3 text-sm font-medium ${
                    currentStep >= step.id ? 'text-education-blue' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </span>
                  {index < steps.length - 1 && (
                    <div className={`w-12 h-0.5 mx-4 ${
                      currentStep > step.id ? 'bg-education-blue' : 'bg-gray-200'
                    }`} />
                  )}
                </div>
              ))}
            </div>
          </CardHeader>

          <CardContent className="p-8">
            {currentStep === 1 && (
              <div className="space-y-6">
                <CardTitle className="text-center mb-8">基本信息</CardTitle>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="childName">孩子姓名</Label>
                    <Input 
                      id="childName"
                      placeholder="请输入孩子姓名"
                      value={formData.childName}
                      onChange={(e) => setFormData({...formData, childName: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="childAge">孩子年龄</Label>
                    <Input 
                      id="childAge"
                      placeholder="请输入年龄"
                      value={formData.childAge}
                      onChange={(e) => setFormData({...formData, childAge: e.target.value})}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="gender">性别</Label>
                    <Select onValueChange={(value) => setFormData({...formData, gender: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="请选择性别" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">男</SelectItem>
                        <SelectItem value="female">女</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="location">目前居住地</Label>
                    <Select onValueChange={(value) => setFormData({...formData, location: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="请选择居住地" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="china">中国</SelectItem>
                        <SelectItem value="usa">美国</SelectItem>
                        <SelectItem value="other">其他</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            )}

            {currentStep === 2 && (
              <div className="space-y-6">
                <CardTitle className="text-center mb-8">教育背景</CardTitle>
                <div className="text-center py-12 text-muted-foreground">
                  <p>教育背景表单内容...</p>
                  <p>（更多表单字段将在此处添加）</p>
                </div>
              </div>
            )}

            {currentStep === 3 && (
              <div className="space-y-6">
                <CardTitle className="text-center mb-8">目标规划</CardTitle>
                <div className="text-center py-12 text-muted-foreground">
                  <p>目标规划表单内容...</p>
                  <p>（更多表单字段将在此处添加）</p>
                </div>
              </div>
            )}

            <div className="flex justify-between items-center mt-8 pt-6 border-t">
              <Button 
                variant="outline" 
                onClick={handlePrev} 
                disabled={currentStep === 1}
                className="flex items-center space-x-2"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>上一步</span>
              </Button>
              
              <Button 
                onClick={handleNext} 
                disabled={currentStep === 3}
                className="bg-education-gradient text-white hover:opacity-90 flex items-center space-x-2"
              >
                <span>下一步</span>
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};

export default CreatePathwaySection;