using System.Activities;
using System.ComponentModel;

namespace codedActivity
{
    [Category("codedActivity")]
    [DisplayName("Say Hello")]
    [Description("Returns a greeting string for a given name.")]
    public sealed class SayHello : CodeActivity
    {
        [Category("Input")]
        [DisplayName("Name")]
        [Description("The name to greet.")]
        [RequiredArgument]
        public InArgument<string> in_Name { get; set; }

        [Category("Output")]
        [DisplayName("Greeting")]
        [Description("The composed greeting.")]
        public OutArgument<string> out_Greeting { get; set; }

        protected override void Execute(CodeActivityContext context)
        {
            var name = in_Name.Get(context);
            out_Greeting.Set(context, $"Hello, {name}!");
        }
    }
}
