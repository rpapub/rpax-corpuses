using System.Activities.DesignViewModels;

namespace codedActivity
{
    public class SayHelloViewModel : DesignPropertiesViewModel
    {
        public DesignInArgument<string> in_Name { get; set; }
        public DesignOutArgument<string> out_Greeting { get; set; }

        public SayHelloViewModel(IDesignServices services) : base(services)
        {
        }

        protected override void InitializeModel()
        {
            base.InitializeModel();
            PersistValuesChangedDuringInit();

            var orderIndex = 0;

            in_Name.DisplayName = "Name";
            in_Name.Tooltip = "The name to greet.";
            in_Name.IsRequired = true;
            in_Name.IsPrincipal = true;
            in_Name.OrderIndex = orderIndex++;

            out_Greeting.DisplayName = "Greeting";
            out_Greeting.Tooltip = "The composed greeting.";
            out_Greeting.IsPrincipal = false;
            out_Greeting.OrderIndex = orderIndex;
        }
    }
}
